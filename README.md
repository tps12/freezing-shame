freezing-shame
==============

Setup with:
```
$ virtualenv -p /path/to/python3 venv
$ venv/bin/activate
$ pip install -r requirements.txt
$ export SECRET_KEY=test
$ python freezing/manage.py syncdb
```

Seed with some random stores and products:
```
$ python freezing/shame/scripts/seed.py
Created oxywelding store
Added diffusor, crappie, collaret, suzerain, filmish, enhorror, vergery, Acemetic, sialorrhea and semball

$ python freezing/shame/scripts/seed.py 
Created systyle store
Added viscus, swine, chuter, Bradshaw, dialogic, rynt, barbone, hiver and poriness

$ python freezing/shame/scripts/seed.py 
Created genesiacal store
Added theodicy, hacking, bulkily, resthouse, thegndom, cedry, quaker, aftershock and chapellany
```

Run locally by adding each store's subdomain to `/etc/hosts`, e.g.:
```
$ for subdomain in oxywelding systyle genesiacal;
> do echo 127.0.0.1 $subdomain.localhost | sudo tee -a /etc/hosts;
> done
```

and then:
```
$ python freezing/manage.py runserver
```
