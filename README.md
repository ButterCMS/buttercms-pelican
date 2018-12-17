# buttercms-pelican
ButterCMS Plugin for Pelican getpelican.com

## Requirements
- buttercms-python


## How to use

You need to clone this repo into your plugin folders, then add "buttercms-pelican" to plugins list in `pelicanconf.py`

```
PLUGIN_PATHS = ["/path/to/plugins"]
PLUGINS = [sitemap", "buttercms-pelican"]
```

Plus, add your butter API key to config:

```
BUTTER_CONFIG = {
    'api_key': 'YourAPIKeyHere'
}
```

Then you can generate your content normally, then post from Butter will be generated like normal posts.

```
pelican content
```



