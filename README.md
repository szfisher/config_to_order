## Config To Order

Config To Order
for more details please kindly refer to https://discuss.erpnext.com/t/new-feature-config-to-order-erpnext-version-of-saps-variant-configuration-need-community-feedback/55621


Here the guidance how to use it

1. install the app by bench

bench get-app config_to_order https://github.com/szfisher/config_to_order.git

bench --site yoursite install-app

2. create new configuration template: custom doctype
   go to doctype list, then new, or directly new doctype, make sure the custom check box activated
   
3. create a configurable item and assign the configuration template
   new item, goto variants section, check is configurable and select the above create new doctype as configuration doctype(template),
   activate checkbox has serial
 
 4. create all other items to be used in the BOM(super BOM)
 
 5. create BOM(super BOM) which includes all possible components with needed selection condition.
    pay attention to following rules 
    5.1 configurable item as BOM header item
    5.2 for bom component, there are 4 new fields available under the configuration section: item from configuration, qty from configuration, desc from configuration and selection condition, the item/qty/desc from configuration maps to the configuration template(doctype) field, selection condition is code field for python expression
       5.2.1 leave both item from configuration and selection condition fields empty makes the component as mandatory component among the final BOM componnents list all the time
       5.2.2 item from configuration allows you selecting a configuration doctype's field, which normally link field with options as Item, (custom script can be used to restrict selecting relevant items by condition like item group), this field is meant to allow selecting item during order processing
       5.2.3 instead of directly allow user selecting item, it is possible to map the user selection (option of the select field) to bom component by python expression in the selection condition field
       5.2.4 qty from configuration is used to allow user specify the needed quantity of the component during configuration
       5.2.5 desc from configuration allows user to input the customer's unique specification of the component, 
  
  6. Configuration - Sales order 
    6.1 select the configurable item, new onfiguration section with configuration and configuration result field are avaiable
    
    6.2 click the config button, there will be a popup window allow you to choose create new configuration or reference existing configuration(by sales order number or the configuration name) to switch to the configuration template form, click save button to return back the item dialog form,
    6.3 click the configuration result button, a popup window which allows you to choose the BOM(super bom) and whether use multi level bom, click make configuraion result goes to the configuration result screen, in which you can review and change the price as needed, click save button goes back to the item dialog form again, the total price of the configuration result will be copied to the rate field.
    6.4 after sales order released, you can create work order like before, the components of the work order are only relevant to the configuration.
   


#### License

MIT
