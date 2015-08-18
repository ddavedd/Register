# Read in lists of form
# the word (category) then category number on first line alone 
# products on first line in order, the number -1 indicates a blank space
# products on second line
# ...
# products on last line
# (all other products in category go after this automatically)
def read_category_order():
   f = open('product_order.txt', 'r')
   lines = f.readlines()
   f.close()

   MAXIMUM_LINE_LENGTH = 10

   current_category = None
   category_dict = {}

   for line in lines:
      clean_line = line.strip()
      line_items = line.split(" ")
      
      if line_items[0].lower() == "cat":
         print "Found category"
         current_category = int(line_items[1])
         category_dict[current_category] = []
      else:
         cast_items = [int(x) for x in line_items if x.strip() != ""]
         if len(cast_items) > MAXIMUM_LINE_LENGTH:
            print "WARNING: Line too long in category %i, shorten list in product_order.txt" % current_category
         if len(cast_items) > 0:
            category_dict[current_category].append(cast_items)
   
   return category_dict
