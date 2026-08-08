source "https://rubygems.org"

gem "jekyll", "~> 4.3"
# NOTE: kramdown.input: GFM in _config.yml needs kramdown-parser-gfm. Do NOT add
# it here: Jekyll 4 already depends on it directly, so it is always in the lock,
# and declaring it changes the Gemfile without changing Gemfile.lock. CI runs
# bundler in frozen mode (bundler-cache: true), which then fails with exit 16.
# Any real Gemfile change must be followed by `bundle lock` and a lock commit.

group :jekyll_plugins do
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
end

# Windows needs timezone data bundled
gem "tzinfo-data", platforms: [:windows]
