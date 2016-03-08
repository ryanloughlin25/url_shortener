# url_shortener

A simple application for creating "shortened" urls.  
Written using flask, sqlalchemy, and postgres hosted on Heroku at https://mighty-oasis-60330.herokuapp.com/

##routes

###GET /\<short_url_hash\>

The main function of the application.  It will redirect to a previously POSTed url.  
  302 if the <short_url_hash> exists  
  404 if not  

###GET /urls/\<short_url_hash\>

Return a json representation of the url resource.  It does not redirect.  
  200 if the \<short_url_hash\> exists  
  404 if not  

###POST /urls

Accepts json with a single property, url, which specifies the url to "shorten".  
Will create a url resource that can be used with the previous two routes.  
The \<short_url_hash\> created for a url resource has a one to one mapping with the url to be "shortened".  
  415 if the request does not contain json  
  422 if the json does not contain a url property  
  409 if the resource already exists  
  201 if the resource is properly created  

###GET /urls

Returns a list of the last 100 url resources created.  

###GET /urls/popular domains

Returns a list of the 10 most popular (popularity is determined by number of visits to urls via /url/\<short_url_hash\>) domains.  
The format for an example domain:  
```
{
  "domain": "www.google.com",
  "numberOfVisits": 50
}
```

##schema
```
      Column      |            Type             |
------------------+-----------------------------+
 id               | integer                     |
 long_url         | text                        |
 short_url_hash   | character varying(6)        |
 domain           | text                        |
 number_of_visits | integer                     |
 created_at       | timestamp without time zone |
 updated_at       | timestamp without time zone |
Indexes:
    "url_pkey" PRIMARY KEY, btree (id)
    "url_short_url_hash_key" UNIQUE CONSTRAINT, btree (short_url_hash)
```
