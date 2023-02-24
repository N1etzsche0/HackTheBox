# Hat Valley - Shop Online!

### To Do
1. Waiting for SQL database to be setup, using offline files for now, will merge with database once it is setup
2. Implement checkout system, link with credit card system (Stripe??)
3. Implement shop filter
4. Get full catalogue of items

### How to Add New Catalogue Item
1. Copy an existing item from /product-details and paste it in the same folder, changing the name to reflect a new product ID
2. Change the fields to the appropriate values and save the file.  
-- NOTE: Please leave the header on first line! This is used to verify it as a valid Hat Valley product. --

### Hat Valley Cart
Right now, the user's cart is stored within /cart, and is named according to the user's session ID. All products are appended to the same file for each user.
To test cart functionality, create a new cart file and add items to it, and see how they are reflected on the store website!
