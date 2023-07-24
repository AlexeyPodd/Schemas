# Schemas site

### About site
Site is a service for generating CSV files with fake (dummy) data using Django and Ajax.

### FakeCSV
User can be created only via admin interface. Any logged-in user can generate and download csv files with any number of columns with different data types.

### Types of data
There is different types of data. Some needs limits set for generating, some uses source file, some are self-sufficient.

## Launch of the project. Testing.
Before running test you should set SECRET_KEY in schemas.settings.py or environment variable SECRET_KEY.
For launching also needed standard manipulations - such as providing migrations, collecting static, creating superuser, etc.
But also for proper functioning of the site you would need to set some Separators in site admin.