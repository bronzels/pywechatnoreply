import mykey

key_path = mykey.__file__
package_key_abs_path = key_path[0:key_path.find('__init__.py')]
package_key_res_path = 'mykey'
