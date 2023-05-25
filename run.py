from app_main import app
import dns.resolver
dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers=['8.8.8.8']

if __name__ == '__main__':
    app.run(debug = True, port = 8000)