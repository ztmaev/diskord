from urllib import parse


token = "MTE0MTAwMDg0MzA3MjY0NzI5MA.G1jGag.htRqZBklgFzeIZI1Ka6xhcRLTW77OtEzN7e1VQ"
client_id = 1141000843072647290
client_secret = "QWVGp6-duEfKk51-cX_fal2Z_EL1GDez"
redirect_uri = "http://localhost:5000/oauth/callback"
oauth_url = f"https://discord.com/api/oauth2/authorize?client_id=1141000843072647290&redirect_uri={parse.quote(redirect_uri)}&response_type=code&scope=identify"

