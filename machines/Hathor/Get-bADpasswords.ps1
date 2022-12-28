type Get-bADpasswords.ps1
 # A few helper functions
#
# Find us here:
# - https://www.improsec.com
# - https://github.com/improsec
# - https://twitter.com/improsec
# - https://www.facebook.com/improsec

# ================ #
# CONFIGURATION => #
# ================ #

# Domain information
$domain_name = "windcorp"
$naming_context = 'DC=windcorp,DC=htb'

# Directories
$group_folder = '.\Accessible\AccountGroups'
$password_folder = '.\Accessible\PasswordLists'

# Logging
$current_timestamp = Get-Date -Format ddMMyyyy-HHmmss

#Actions if password is weak
# - resetPWd = Resets the users password to a random password
# - removeNoExpire = Unticks "Password never expires"
# - changePassLogon = Ticks the "The user must change password on next logon"
#
#IMPORTANT: If resetPwd is enabled, the users password will be changed to a random password.
#That password are logged in logfile, so remember to delete the logs.

$resetPwd = $false 
$removeNoExpire = $false
$changePassLogon = $false

$log_filename  = ".\Accessible\Logs\log_$domain_name-$current_timestamp.txt"
$csv_filename  = ".\Accessible\CSVs\exported_$domain_name-$current_timestamp.csv"

$write_to_log_file = $true
$write_to_csv_file = $true
$write_hash_to_logs = $true

# Result email dispatch information
# Email username and password are collected by a prompt on first run and saved securely in the users %userprofile/%/Documents/Credentials folder, protected by Microsoft DPAPI.
# The location can be changed by enabling and changing the variable: $cred_storepath
# https://bitbucket.org/metisit/credentialmanager/src/master/
# To re-set username and password, just delete the files named: bADpasswords.password and bADpasswords.username
# If you are running this script scheduled from another account, you will find istructions how to create credential-files inside the module: CredentialManager.psm1   

#$cred_storepath = "c:\Credentials\myname"
$mail_authenticate = $true
$mail_smtp = "mail.windcorp.htb"
$mail_recipient = "Get-bADpassword <admin@windcorp.htb>"
$mail_sender = "Get-bADpasswords <badadpa@nwindcorp.htb>"
$mail_subject = "Get-bADpasswords $($domain_name.ToUpper()) $current_timestamp"
$mail_port = 587
$Enablessl = $true

$send_log_file = $true
$send_csv_file = $false

# ================ #
# PREPROCESSING => #
# ================ #

Add-Type -AssemblyName System.Web
Import-Module ./CredentialManager.psm1

$creds = Get-StoredCredential -Name bADpasswords -StorePath $cred_storepath 

$current_directory = Split-Path $MyInvocation.MyCommand.Path
[System.IO.Directory]::SetCurrentDirectory($current_directory) > $null

[System.IO.Directory]::CreateDirectory('.\Accessible\Logs') > $null
[System.IO.Directory]::CreateDirectory('.\Accessible\CSVs') > $null

$psi_library_path = '.\\PSI\\'
$psi_repacker_path = '.\PSI\'

if ([System.Environment]::Is64BitOperatingSystem -and [System.Environment]::Is64BitProcess) {
	$psi_library_path += 'Psi_x64.dll'
	$psi_repacker_path += 'PsiRepacker_x64.exe'
} else {
	$psi_library_path += 'Psi_x86.dll'
	$psi_repacker_path += 'PsiRepacker_x86.exe'
}

# include helper files
. '.\Helper_Logging.ps1'
. '.\Helper_Passwords.ps1'

# ================ #
# VARIABLES =====> #
# ================ #

# constant(s)
$empty_nt_hash = '31d6cfe0d16ae931b73c59d7e0c089c0'
                  
# miscellaneous
$script_name = 'Get-bADpasswords'
$script_version = '3.03'

# ================ #
# FUNCTIONS =====> #
# ================ #

function Get-AliveDomainController {
    param (
        [Parameter(Mandatory=$true, Position=0)]
        $name
    )

    $context_type = [System.DirectoryServices.ActiveDirectory.DirectoryContextType]::Domain
    $domain_context = [System.DirectoryServices.ActiveDirectory.DirectoryContext]::new($context_type, $name);
    $domain_controllers = [DirectoryServices.ActiveDirectory.Domain]::GetDomain($domain_context).FindAllDomainControllers();

    if (!($domain_controllers)) {
        return $null
    } else {
        foreach ($domain_controller in $domain_controllers) {
            if (Test-Connection $domain_controller.Name -Count 1) {
                return $domain_controller.Name
            }
        }
    }
}








# ================ #
# SCRIPT ========> #
# ================ #


clear

Log-Automatic -string "Version:`t'$script_name v$script_version'." -type 'info' -timestamp
Log-Automatic -string "Log file:`t'$log_filename'." -type 'info' -timestamp
Log-Automatic -string "CSV file:`t'$csv_filename'." -type 'info' -timestamp

if ($write_hash_to_logs) {
    Log-Specific -filename $csv_filename -string "Activity;Password Type;Account Type;Account Name;Account SID;Account password hash;Present in password list(s)"
} else {
    Log-Specific -filename $csv_filename -string "Activity;Password Type;Account Type;Account Name;Account SID;Present in password list(s)"
}

# =========== Query domain data ===========
$domain_controller_fqdn = Get-AliveDomainController -name $domain_name

if (!($domain_controller_fqdn)) {
    Log-Automatic -string "A live Domain Controller in '$domain_name' was not found. Exiting." -type 'info' -timestamp
    exit
}

$domain_controller = $domain_controller_fqdn.Split('.')[0]

# =========== Repack password files ===========
Log-Automatic -string "Testing versioning for files in '$password_folder'..." -type 'info' -timestamp
Get-RepackFiles -files (Get-ChildItem $password_folder -Filter '*.txt')

# =========== Query AD user data ===========
Log-Automatic -string "Replicating AD user data with parameters (DC = '$domain_controller', NC = '$naming_context')..." -type 'info' -timestamp

$ad_users = $null

try {
    $ad_users = Get-ADReplAccount -All -Server $domain_controller -NamingContext $naming_context | where { $_.SamAccountType -eq 'User' } | select SamAccountName,SID,Enabled,@{ N="NtHash"; E={ ConvertTo-Hex $_.NTHash }},@{ N="Activity"; E={ if ($_.Enabled) { 'active' } else { 'inactive' } }},@{ N="PrivilegeType"; E={ 'regular' }}

} catch {
	Log-Automatic -string $_.Exception.Message -type 'fail' -timestamp
	exit
}

if (($ad_users -eq $null) -or ($ad_users.Count -le 0)) {
	Log-Automatic -string "The AD returned no users - no comparisons can be performed." -type 'fail' -timestamp
    exit
} else {
	Log-Automatic -string "The AD returned $($ad_users.count) users." -type 'info' -timestamp
    
    foreach ($group_file in (Get-ChildItem $group_folder -Filter '*.txt')) {
        foreach ($group in (Get-Content -Path $group_file.FullName)) {
            $group_identity = ($group_file.BaseName -split ' - ')[1].ToLower()
            $members = Get-ADGroupMember -Identity $group -Recursive | select -ExpandProperty SID

            foreach ($user in $ad_users) {
                if (($members -contains $user.SID) -and ($user.PrivilegeType -eq 'regular')) {
                    $user.PrivilegeType = $group_identity
                }
            }
        }
    }
}

# =========== Test for empty / weak passwords ===========
$users_with_empty_password = @($ad_users | where { ($_.NtHash -ne $null) -and ($_.NtHash -eq $empty_nt_hash) })
$users_with_valid_password = @($ad_users | where { ($_.NtHash -ne $null) -and ($_.NtHash -ne $empty_nt_hash) })

[System.Collections.ArrayList]$user_hashes = @()

foreach ($user in $users_with_valid_password) {
    if ($user_hashes.Contains($user.NtHash) -eq $false) {
        $user_hashes.Add($user.NtHash) > $null
    }
}

$files = (Get-ChildItem $password_folder -Filter '*.bin').FullName
$results = @()

Test-Passwords -sources $files -hashes $user_hashes -results ([ref]$results) > $null

$user_matches = @()

foreach ($result in $results) {
    $pair = $result -split '\;'
    $user_matches += @($users_with_valid_password | where { $_.NtHash -eq $pair[0] } | select Enabled,Activity,PrivilegeType,SamAccountName,SID,NtHash,@{ N="PasswordFiles"; E={ @($pair[1] -split '\|') }})
}

$file_matches = @{}

foreach ($user in $user_matches) {
    foreach ($file in $user.PasswordFiles) {
        $filename = (Get-Item -Path $file).BaseName

        if ($file_matches.Keys -notcontains $filename) {
            $file_matches[$filename] = @()
        }
        
        $file_matches[$filename] += @($user)
    }
}

# =========== Test for shared passwords ===========
$shared_passwords = $users_with_valid_password | group -Property NtHash | where { $_.Count -gt 1 } | sort -Descending -Property Count | select Count,@{N="Enabled";E={ $_.Group.Enabled }},@{N="Activity";E={ $_.Group.Activity }},@{N="PrivilegeType";E={ $_.Group.PrivilegeType }},@{N="SamAccountName";E={ $_.Group.SamAccountName }},@{N="SID";E={ $_.Group.SID }},@{N="NtHash";E={ $_.Name }}
$shared_passwords_info = $shared_passwords | measure -Property Count -Sum

# =========== Report results ===========
if (($users_with_empty_password -ne $null) -and ($users_with_empty_password.Count -gt 0)) {
	Log-Automatic -string "Found $($users_with_empty_password.Count) user(s) with empty passwords." -type 'info' -timestamp

    foreach ($user in $users_with_empty_password) {
	    Log-Automatic -string "Empty password found for user '$($user.SamAccountName)'." -type 'info' -timestamp

	    if ($write_to_csv_file) {
            Log-Specific -filename $csv_filename -string "$($user.Activity);empty;$($user.PrivilegeType);$($user.SamAccountName);$($user.SID)"
	    }
    }
}

if (($user_matches -ne $null) -and ($user_matches.Count -gt 0)) {
	Log-Automatic -string "Found $($user_matches.Count) user(s) with weak passwords." -type 'info' -timestamp

    # =========== Actions if password is weak
    foreach ($user in $user_matches) {
        $files = "'$((Get-Item -Path $user.PasswordFiles).BaseName -join ""','"")'"
        $newpass = [System.Web.Security.Membership]::GeneratePassword(15,1)
	    Log-Automatic -string "Matched password found for user '$($user.SamAccountName)' in list(s) $files." -type 'info' -timestamp
        if ($resetPwd){
            net user /domain $($user.SamAccountName) $newpass
            Log-Automatic -string "'$($user.SamAccountName)':$newpass" -type 'info' -timestamp
        }

        if ($removeNoExpire){
            Set-ADUser -Identity $($user.SamAccountName) -PasswordNeverExpires:$FALSE
        }

        if ($changePassLogon){
            Set-Aduser -Identity $($user.SamAccountName) -ChangePasswordAtLogon $true
        }
        
	    if ($write_to_csv_file) {
            if ($write_hash_to_logs) {
		        Log-Specific -filename $csv_filename -string "$($user.Activity);weak;$($user.PrivilegeType);$($user.SamAccountName);$($user.SID);$($user.NtHash);$files"
            } else {
		        Log-Specific -filename $csv_filename -string "$($user.Activity);weak;$($user.PrivilegeType);$($user.SamAccountName);$($user.SID);$files"
            }
	    }
    }
}

if (($shared_passwords -ne $null) -and ($shared_passwords.Count -gt 0)) {
	Log-Automatic -string "Found $($shared_passwords_info.Sum) user(s) sharing $($shared_passwords_info.Count) passwords." -type 'info' -timestamp

    foreach ($password in $shared_passwords) {
        $names = "'$($password.SamAccountName -join ""','"")'"

        if ($write_hash_to_logs) {
	        Log-Automatic -string "Hash '$($password.NtHash)' is shared by user(s): $names." -type 'info' -timestamp
        } else {
	        Log-Automatic -string "A single hash is shared by user(s): $names." -type 'info' -timestamp
        }

	    if ($write_to_csv_file) {
            for ($i = 0; $i -lt $password.Count; $i++) {
                if ($write_hash_to_logs) {
    		        Log-Specific -filename $csv_filename -string "$($password.Activity[$i]);shared;$($password.PrivilegeType[$i]);$($password.SamAccountName[$i]);$($password.SID[$i]);$($password.NtHash)"
                } else {
    		        Log-Specific -filename $csv_filename -string "$($password.Activity[$i]);shared;$($password.PrivilegeType[$i]);$($password.SamAccountName[$i]);$($password.SID[$i])"
                }
            }
	    }
    }
}

Log-Automatic -string "Found a total of '$($users_with_empty_password.Count)' user(s) with empty passwords" -type 'info' -timestamp
Log-Automatic -string "Found a total of '$($user_matches.Count)' user(s) with weak passwords" -type 'info' -timestamp
Log-Automatic -string "Found a total of '$($shared_passwords_info.Sum)' user(s) with shared passwords" -type 'info' -timestamp

# =========== Dispatch email results ===========
$mail_body = "Total users: '$($ad_users.count)'`n"
$mail_body += "Amount of total users found with empty passwords: '$($users_with_empty_password.Count)' ($([Math]::round(($users_with_empty_password.Count / $ad_users.Count) * 100, 2))%)`n"
$mail_body += "Amount of total users found with weak passwords: '$($user_matches.Count)' ($([Math]::round(($user_matches.Count / $ad_users.Count) * 100, 2))%)`n"

foreach ($file in $file_matches.GetEnumerator()) {
    $mail_body += "`tFrom password list '$($file.Name)': $($file.Value.Count)`n"
}

$mail_body += "Number of total users sharing passwords: '$($shared_passwords_info.Sum)' ($([Math]::round(($shared_passwords_info.Sum / $ad_users.Count) * 100, 2))%)`n"
$mail_body += "Number of total unique passwords shared: '$($shared_passwords_info.Count)'`n`n"

# =========== Active / Inactive users ===========
$active_shared = 0
$inactive_shared = 0

foreach ($password in $shared_passwords) {
    for ($i = 0; $i -lt $password.Count; $i++) {
        if ($password.Enabled[$i] -eq $true) {
            $active_shared = $active_shared + 1
        } else {
            $inactive_shared = $inactive_shared + 1
        }
    }
}

# =========== Active users ===========
$active_empty = @($users_with_empty_password | where { $_.Enabled -eq $true })
$active_match = @($user_matches | where { $_.Enabled -eq $true })

$mail_body += "Total active users: '$(($ad_users | where { $_.Enabled -eq $true }).count)'`n"
$mail_body += "Amount of active users found with empty passwords: '$($active_empty.Count)' ($([Math]::round(($active_empty.Count / $ad_users.Count) * 100, 2))%)`n"
$mail_body += "Amount of active users found with weak passwords: '$($active_match.Count)' ($([Math]::round(($active_match.Count / $ad_users.Count) * 100, 2))%)`n"

foreach ($file in $file_matches.GetEnumerator()) {
    $active_file = @($file.Value | where { $_.Enabled -eq $true })

    if ($active_file.Count -gt 0) {
        $mail_body += "`tFrom password list '$($file.Name)': $($active_file.Count)`n"
    }
}

$mail_body += "Number of active users sharing passwords: '$($active_shared)' ($([Math]::round(($active_shared / $ad_users.Count) * 100, 2))%)`n`n"

# =========== Inactive users ===========
$inactive_empty = @($users_with_empty_password | where { $_.Enabled -eq $false })
$inactive_match = @($user_matches | where { $_.Enabled -eq $false })

$mail_body += "Total inactive users: '$(($ad_users | where { $_.Enabled -eq $false }).count)'`n"
$mail_body += "Amount of active users found with empty passwords: '$($inactive_empty.Count)' ($([Math]::round(($inactive_empty.Count / $ad_users.Count) * 100, 2))%)`n"
$mail_body += "Amount of active users found with weak passwords: '$($inactive_match.Count)' ($([Math]::round(($inactive_match.Count / $ad_users.Count) * 100, 2))%)`n"

foreach ($file in $file_matches.GetEnumerator()) {
    $inactive_file = @($file.Value | where { $_.Enabled -eq $false })

    if ($inactive_file.Count -gt 0) {
        $mail_body += "`tFrom password list '$($file.Name)': $($inactive_file.Count)`n"
    }
}

$mail_body += "Number of inactive users sharing passwords: '$($inactive_shared)' ($([Math]::round(($inactive_shared / $ad_users.Count) * 100, 2))%)`n`n"

# =========== Shared passwords ===========
if (($users_with_empty_password -ne $null) -and ($users_with_empty_password.Count -gt 0)) {
    $mail_body += "Users with empty passwords:`n"
    $mail_body += "$($users_with_empty_password.SamAccountName -join ""`n"")`n`n"
}

if (($user_matches -ne $null) -and ($user_matches.Count -gt 0)) {
    $mail_body += "Users with weak passwords:`n"
    $mail_body += "$($user_matches.SamAccountName -join ""`n"")`n`n"
}

if (($shared_passwords -ne $null) -and ($shared_passwords.Count -gt 0)) {
    $mail_body += "Users with shared passwords:`n"

    $tmp = 1

    foreach ($password in $shared_passwords) {
        $mail_body += "$($tmp): '$($password.SamAccountName -join ""','"")'`n"
        $tmp++;
    }
}


# Send mail
$Message = New-Object System.Net.Mail.MailMessage $mail_sender,$mail_recipient

if ($send_log_file) {
    $Message.Attachments.Add($log_filename)
   }

if ($send_csv_file) {
    $Message.Attachments.Add($csv_filename)
}

$Message.IsBodyHTML = $true
$Message.Subject = $mail_subject
$Message.Body = $mail_body
$Smtp = New-Object Net.Mail.SmtpClient($mail_smtp,$mail_port)
$Smtp.EnableSsl = $Enablessl
if ($mail_authenticate){

    $Smtp.Credentials = $creds
} 
$Smtp.Send($Message)



exit
 

# SIG # Begin signature block
# MIIIbwYJKoZIhvcNAQcCoIIIYDCCCFwCAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUUGZp8caGy/i0f4q5GgmPVLHR
# eJ+gggXTMIIFzzCCBLegAwIBAgITIAAAAAVE7aootjbd3AAAAAAABTANBgkqhkiG
# 9w0BAQsFADBOMRMwEQYKCZImiZPyLGQBGRYDaHRiMRgwFgYKCZImiZPyLGQBGRYI
# d2luZGNvcnAxHTAbBgNVBAMTFHdpbmRjb3JwLUhBVEhPUi1DQS0xMB4XDTIyMDMx
# ODA5MDMxMVoXDTMyMDMxNTA5MDMxMVowVzETMBEGCgmSJomT8ixkARkWA2h0YjEY
# MBYGCgmSJomT8ixkARkWCHdpbmRjb3JwMQ4wDAYDVQQDEwVVc2VyczEWMBQGA1UE
# AxMNQWRtaW5pc3RyYXRvcjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB
# ANymPv5/lrOiEd/O1SOIE+JJv48MrY41Ev6YrS5tI97LA4KKDciMTEk/FBMSIPWe
# Rcmn3lk3z8bYHJP75QjmqXgFAvwUuknwSFMuZ8gU8CxVAEGeUAk+2oJ7tBUds931
# i2jG/9DTLxDiCV0L7aNLyIHIh0fYNt33iFlXgNtA/Mc4oWqLK7aha/4CXhbbQTiu
# FYqxWZrrOU+iyHfuCcnArka2/iRUT8VvmJqJEXsrO+fQcOvI/n2YgU+kQ6Vw0zQk
# 5AX8C2fNPWTeRD5kgULe0SduL8yCF7tercNkaqEZx5PIR/+GI3yJg7Crn2qRYJ40
# IYRKiGnJWZLJteEa8+CUv1kCAwEAAaOCApswggKXMD0GCSsGAQQBgjcVBwQwMC4G
# JisGAQQBgjcVCILUznCD1qdohvWREYToiS+G+41kgSqBkDyC69BtAgFlAgEAMBMG
# A1UdJQQMMAoGCCsGAQUFBwMDMA4GA1UdDwEB/wQEAwIHgDAbBgkrBgEEAYI3FQoE
# DjAMMAoGCCsGAQUFBwMDMB0GA1UdDgQWBBT9pA1L7J29t3kN+MOVXpVejV/eNjAf
# BgNVHSMEGDAWgBTxjkqkbc2CsGldYvNjmn6LbnL2WTCB0gYDVR0fBIHKMIHHMIHE
# oIHBoIG+hoG7bGRhcDovLy9DTj13aW5kY29ycC1IQVRIT1ItQ0EtMSxDTj1oYXRo
# b3IsQ049Q0RQLENOPVB1YmxpYyUyMEtleSUyMFNlcnZpY2VzLENOPVNlcnZpY2Vz
# LENOPUNvbmZpZ3VyYXRpb24sREM9d2luZGNvcnAsREM9aHRiP2NlcnRpZmljYXRl
# UmV2b2NhdGlvbkxpc3Q/YmFzZT9vYmplY3RDbGFzcz1jUkxEaXN0cmlidXRpb25Q
# b2ludDCBxwYIKwYBBQUHAQEEgbowgbcwgbQGCCsGAQUFBzAChoGnbGRhcDovLy9D
# Tj13aW5kY29ycC1IQVRIT1ItQ0EtMSxDTj1BSUEsQ049UHVibGljJTIwS2V5JTIw
# U2VydmljZXMsQ049U2VydmljZXMsQ049Q29uZmlndXJhdGlvbixEQz13aW5kY29y
# cCxEQz1odGI/Y0FDZXJ0aWZpY2F0ZT9iYXNlP29iamVjdENsYXNzPWNlcnRpZmlj
# YXRpb25BdXRob3JpdHkwNQYDVR0RBC4wLKAqBgorBgEEAYI3FAIDoBwMGkFkbWlu
# aXN0cmF0b3JAd2luZGNvcnAuaHRiMA0GCSqGSIb3DQEBCwUAA4IBAQB2sQJBWW1j
# jyMof10cc6Mub35/KeymbOp+WMVVp5DG1gyIIHHqiHy3TMiZduP2COGsAGAL51GZ
# Tj2OEkgzQGhDM1M+s2ajwFtrgxoV9EJTbFfjA82jT7AO+e7ApHpOPXp/TzmBLIH8
# wvHky43pE+JKYtK/NFPCeJh6LWoe9o0x6A9mOngWhbzFU21Prag6jbe/A1oKGUEg
# IpaWeG0kl/ppleyMU3hEB8NlYvbbS2QrYoDzlb4stmQQwqXjprvao9fxUjywS8Ze
# ik3CRxAJF6FAZ12sDy6QhhJ3aP54w09MTmjjsd3wFcsgWOSkK+JRP+H8DdZGwscz
# CwTdAVSxm6AhMYICBjCCAgICAQEwZTBOMRMwEQYKCZImiZPyLGQBGRYDaHRiMRgw
# FgYKCZImiZPyLGQBGRYId2luZGNvcnAxHTAbBgNVBAMTFHdpbmRjb3JwLUhBVEhP
# Ui1DQS0xAhMgAAAABUTtqii2Nt3cAAAAAAAFMAkGBSsOAwIaBQCgeDAYBgorBgEE
# AYI3AgEMMQowCKACgAChAoAAMBkGCSqGSIb3DQEJAzEMBgorBgEEAYI3AgEEMBwG
# CisGAQQBgjcCAQsxDjAMBgorBgEEAYI3AgEVMCMGCSqGSIb3DQEJBDEWBBQid53e
# JHENiNYfjP77T2vYIXwb8jANBgkqhkiG9w0BAQEFAASCAQC5rn9RHanHzkLEPEBu
# UKkin9ZGaInMUzcF2+VMzHbCRmD8KAYFcPfrvaQE3f9i3m/fC/tmoEGepSMR8puz
# UOfSS/w2neki7KsqtimYsyZtmMXuAemtI94o8F/kfy5m9DsJzQ851j+xjZf8I6rl
# sHcB0S1PhI2O/eRosm5rGi0PGo0Ibivta1KbsqF1s6ecdCRUL71PR2cw9tR+8CxE
# 3c+VcMj8Qbh6bktI2l4Wz7UOMqy6gS3xlp29lRPK6JnwMZFDGsgzu6mhyJn/67MW
# yMFxE9W0ENJq3FG/ehjV+xSo2ybr35CozLgG0rRM17Lcony9NRYVLF/m3aJj32qY
# e+Jx
# SIG # End signature block
