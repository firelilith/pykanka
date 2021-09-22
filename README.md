# pykanka

My attempt at creating a python API wrapper for the worldbuilding software [Kanka](https://kanka.io). 

pykanka currently  provides get/post/patch functionality  as well as classes for the different entity types found on Kanka. A basic documentation is available through the wiki, here: https://github.com/thatGuySpectre/pykanka/wiki

### Installation

To install pykanka, you can simply use pip to install from github:

`pip install git+https://github.com/thatGuySpectre/pykanka@master`

***

Both this module and the Kanka API itself are prone to changes, so I cannot guarantee stability.

For questions and issues I can be contacted as Spectre#9477 on discord.

I am in no way affiliated with Kanka or its developers.

Have fun :D


***

### Currently Supported

|                     	| GET 	| POST 	| PATCH 	| PUT 	| DELETE 	|
|---------------------	|-----	|------	|-------	|-----	|--------	|
| Abilities           	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Calendars           	| Yes 	| Yes  	| Yes   	| Yes 	| No*   	|
| Characters          	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Events              	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Families            	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Items               	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Journal             	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Locations           	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Maps                	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Map Elements        	| No  	| No   	| No    	| No  	| No     	|
| Notes               	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Organisations       	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Organisation Member 	| No  	| No   	| No    	| No  	| No     	|
| Quests              	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Races               	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Timelines           	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|
| Tags                	| Yes 	| Yes  	| Yes   	| Yes 	| Yes    	|

\*Most likely a serverside error, code 500

I haven't managed to test all fields for posting, if you run into any issues, please contact me here or on discord.

