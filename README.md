# buttercms-pelican
ButterCMS Plugin for Pelican getpelican.com

## Important Notice
This project was created as an example use case of ButterCMS in conjunction with the Pelican static site generator and will not be actively maintained. 

If you’re interested in exploring the best, most up-to-date way to integrate Butter into Python based frameworks like Pelican, you can check out the following resources:

### Starter Projects

The following turn-key starters are fully integrated with dynamic sample content from your ButterCMS account, including main menu, pages, blog posts, categories, and tags, all with a beautiful, custom theme with already-implemented search functionality. All of the included sample content is automatically created in your account dashboard when you sign up for a free trial of ButterCMS.
- [Python Starter](https://buttercms.com/starters/python-starter-project/)
- [Angular Starter](https://buttercms.com/starters/angular-starter-project/)
- [React Starter](https://buttercms.com/starters/react-starter-project/)
- [Vue.js Starter](https://buttercms.com/starters/vuejs-starter-project/)
- Or see a list of all our [currently-maintained starters](https://buttercms.com/starters/). (Over a dozen and counting!)

### Other Resources
- Check out the [official ButterCMS Docs](https://buttercms.com/docs/)
- Check out the [official ButterCMS API docs](https://buttercms.com/docs/api/)


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



