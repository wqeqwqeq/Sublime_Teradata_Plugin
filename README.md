# Sublime_Teradata_Plugin
Local Teradata friend with Query run and auto complete. An in-house solution to replace Teradata SQL Assistant

Major benefit compare to Teradata SQL Assistant
1. Comprehensive autocomplete in keyword and metadata in EDW
2. Metadata completion granularity reaches to column level in EDW, data type also included; completion can also be triggered from an alias 
3. Able to run query directly from sublime, and show result in a read-only Postgre-sql stype output panel, which is easy to navigate and share
4. Can store query result into cache, show result from same query without another round of execution (user can tweak #cache query)
5. Automatically add keyword SAMPLE in the end for easier data exploration (user can define number of rows and overwrite by explicitly type sample)
6. Show exact query execution time and option to stop query 
7. Short cut to select current query and format current query (where cursor stop)
8. Can also be extended if onboarding with snowflake, EDL (As long as we can use python to query from local)
9. Never need to login and autosave query, no need to worry when close file 
10. User can set a timeout to stop query takes super long 

## Install
There are many ways to install, in one word is git clone this package in your sublime package folder, you can open your sublime package folder thru preferences==>"Browse Pakcages"

Once you done, you should find the plugin is in package folder


#### Git clone
1. Open cmd (a windows cmd) and change directory to sublime packages
```
cd C:\Users\282710\AppData\Roaming\Sublime Text\Packages
```
2. clone repo  

#### Direct Download
Download directly and unzip everything, paste the entire folder to sublime package path, make sure the package named exactly as **Sublime_Teradata_Plugin**


#### An extra plugin to install 
Besides git clone above package, there one extra sublime package plugin/package need to install. 

Open _Package control: install packages_, install SQLTool like this 


## Keybind and Setting 


Keybind explain

1. Query execution keybinding 
  * `["ctrl+e", "ctrl+e"]` execute the query 
    * `limit:` stands for number of rows to be returned (in this case, means automatically add sample 100 in the end), can be overwrite if pass sample explicitly
    * `number_of_cache_query:` number of cache query stored. More cache and larger data stored in cache may slow down the plugin
    * `timeout:` query will automatically timeout after 30 seconds
    
 * `["ctrl+q"]` select current query (how it works is select query btw two ";", where cursor stops. Except for the first ";" )
 * `["ctrl+e", "ctrl+b"]` format select query
 * `["ctrl+e", "ctrl+i"]` interrupt running query
 * `["ctrl+e", "ctrl+c"]` clean cached query result
2. Metadata/autocomplete management keybinding
 * `["ctrl+m", "ctrl+p"]` setup teradata username and password
 * `["ctrl+m", "ctrl+i"]` init setup autocomplete, will grab **all** db,tbl,columns that user has *retrieve/select* access into a autocompletion connection group
 * `["ctrl+m", "ctrl+a"]` add a list of tables as a connection group to enable autocomplete 
 * `["ctrl+m", "ctrl+s"]` select specific autocomplete connection group
 * `["ctrl+m", "ctrl+d"]` remove specific autocomplete connection group
 * `["ctrl+m", "ctrl+o"]` open current using autocomplete connection group
 * `["ctrl+m", "ctrl+b"]` browse all the columns that user has *retrieve/select* access, and autocomplete as a query if hit enter
 * `["ctrl+m", "ctrl+r"]` restart connection

## Use
### Elmemtary use
#### Setup username and metadata (One time job)
1. Use `["ctrl+m", "ctrl+p"]` to setup Teradata username and password, after setup, close sublime and relaunch. Try this command again to check if you can see this! 

2. Use `["ctrl+m", "ctrl+i"]` to grab all the columns into metadata autocomplete in EDW that you have select access. For mine, it takes 3 min to grab 300k+ number of columns
#### Setup sublime syntax
Hit `["ctrl+shift+p]` to open command pallet, and type sql, choose _Set syntax: SQL_ and press enter

Alternatively, choose syntax at left bottom, left click and then select SQL. **This plugin will only be functional when the syntax is SQL**


#### Trigger autocomplete 
There multiple way to trigger autocomplete
1. Hit `["ctrl+space"]` to check all possible autocomplete item, use arrow key to navigate, and hit `tab` to autocomplete. In case a _database_ or _column_ autocomplete, enter `.` to trigger autocomplete in next level 
2. Type word and if the input match some part of the autocomplete, you will see the autocomplete pallet while you are typing
3.  Hit `["ctrl+m" , "ctrl+b"]` to show all the columns under current connection group, use arrow key to navigate and hit enter for column you are interested 
4.  Alias auto complete. **Method 1 and 3** can create autocomplete with table's alias automatically. But if you manual type query, you have to type `as` between table and alias in order to update alias-table mapping on the backend 
In case alias overwrite by other query, manually retype `as alias` after the table you want to point to reassign alias to a given table 

#### Run query
1. **Remember to put a semicolon (`;`) at the end of each query!** Semicolon is the separator between queries.
2. You can select your _current query_ (where your current cursor stops) by hit `["ctrl+q"]`. It will won't work as expected if `;` missed at the end of the query
3. Hit `["ctrl+e","ctrl+e"]` to run selected query. Currently only supported run one query at a time 

#### Debug & troubleshooting
For most of time, if you don't see sublime return anything back, a relaunch will fix the problem.

If still sublime does not return anything back, open _teradata sql assistant_ and run the same query, see if it doesn't return anything as well. If you see result return from teradata SQL server, but not from sublime after relaunch, re-download this repo, maybe the bug is fixed in newest commit. 

If relaunch, restart, redownload all failed, congratulation, you spot a new bug! Contact [Stanley](mailto:wqeqsada2131@gmail.com?subject=[Sublime_Teradata_Plugin]%20%20Bug%20Report%20)!

### Advanced Use
For advanced use like 
* add/remove connection group
* interrup query, manage cache/timeout/# rows return
* customizing output pannel
* setup your own keyword autocomplete snippet
* setup your connection point to other edw instance like tdprod2
* restart connection 
* contributing this plugin
* future functionality like connect to snowflake or EDL...

Contact [Stanley](mailto:wqeqsada2131@gmail.com?subject=[Sublime_Teradata_Plugin]%20%20Collab%20)! Collab, bugs and suggestions are welcomed:)


