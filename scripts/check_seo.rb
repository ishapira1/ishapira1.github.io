#!/usr/bin/env ruby

require "json"
require "nokogiri"
require "nokogiri/html5"
require "pathname"
require "uri"

build_dir = File.expand_path(ARGV.fetch(0, "_site"))
abort "Build directory does not exist: #{build_dir}" unless Dir.exist?(build_dir)

site_origin = "https://www.itai-shapira.com"
site_hosts = ["www.itai-shapira.com", "itai-shapira.com"].freeze
errors = []

core_pages = {
  "index.html" => "#{site_origin}/",
  "research/index.html" => "#{site_origin}/research/",
  "projects/index.html" => "#{site_origin}/projects/",
  "cv/index.html" => "#{site_origin}/cv/",
  "privacy/index.html" => "#{site_origin}/privacy/"
}.freeze

redirect_pages = {
  "about/index.html" => "#{site_origin}/",
  "publications/index.html" => "#{site_origin}/research/",
  "portfolio/index.html" => "#{site_origin}/projects/",
  "resume.html" => "#{site_origin}/cv/",
  "terms/index.html" => "#{site_origin}/privacy/"
}.freeze

def read_html(path)
  File.binread(path).force_encoding(Encoding::UTF_8)
end

def parse_html(path)
  Nokogiri::HTML5.parse(read_html(path))
end

def json_objects(value, objects = [])
  case value
  when Hash
    objects << value
    value.each_value { |child| json_objects(child, objects) }
  when Array
    value.each { |child| json_objects(child, objects) }
  end
  objects
end

def local_target_exists?(build_dir, path)
  decoded = URI::DEFAULT_PARSER.unescape(path.to_s)
  decoded = "/" if decoded.empty?
  relative = decoded.sub(%r{\A/+}, "")
  candidates = if relative.empty?
                 ["index.html"]
               elsif decoded.end_with?("/")
                 [File.join(relative, "index.html")]
               elsif File.extname(relative).empty?
                 [relative, "#{relative}.html", File.join(relative, "index.html")]
               else
                 [relative]
               end

  candidates.any? do |candidate|
    expanded = File.expand_path(candidate, build_dir)
    expanded.start_with?("#{build_dir}/") && File.exist?(expanded)
  end
end

html_files = Dir.glob(File.join(build_dir, "**", "*.html")).sort
errors << "No generated HTML files found" if html_files.empty?

html_files.each do |path|
  relative = Pathname.new(path).relative_path_from(Pathname.new(build_dir)).to_s
  source = read_html(path)
  doc = Nokogiri::HTML5.parse(source)

  errors << "#{relative}: references removed /feed.xml" if source.include?("/feed.xml")
  if source.match?(%r{https://(?:www\.)?itai-shapira\.com//})
    errors << "#{relative}: contains a same-domain double-slash URL"
  end

  robots = doc.at_css('meta[name="robots"]')&.[]("content").to_s.downcase
  indexable = !robots.include?("noindex")

  if indexable
    {
      "title" => doc.css("title"),
      "canonical URL" => doc.css('link[rel="canonical"]'),
      "meta description" => doc.css('meta[name="description"]'),
      "Open Graph description" => doc.css('meta[property="og:description"]'),
      "Open Graph image" => doc.css('meta[property="og:image"]'),
      "Open Graph type" => doc.css('meta[property="og:type"]')
    }.each do |label, nodes|
      errors << "#{relative}: expected exactly one #{label}, found #{nodes.length}" unless nodes.length == 1
    end

    description = doc.at_css('meta[name="description"]')&.[]("content").to_s.strip
    og_description = doc.at_css('meta[property="og:description"]')&.[]("content").to_s.strip
    og_image = doc.at_css('meta[property="og:image"]')&.[]("content").to_s.strip
    og_type = doc.at_css('meta[property="og:type"]')&.[]("content").to_s.strip
    canonical = doc.at_css('link[rel="canonical"]')&.[]("href").to_s.strip

    errors << "#{relative}: empty meta description" if description.empty?
    errors << "#{relative}: Open Graph description does not match meta description" unless og_description == description
    errors << "#{relative}: invalid Open Graph image #{og_image.inspect}" unless og_image.start_with?("#{site_origin}/")
    errors << "#{relative}: invalid Open Graph type #{og_type.inspect}" unless %w[website article].include?(og_type)
    errors << "#{relative}: invalid canonical URL #{canonical.inspect}" unless canonical.start_with?(site_origin) && !canonical.match?(%r{\.com//})

    parsed_json = []
    doc.css('script[type="application/ld+json"]').each do |node|
      begin
        parsed_json << JSON.parse(node.text)
      rescue JSON::ParserError => e
        errors << "#{relative}: invalid JSON-LD (#{e.message})"
      end
    end

    objects = parsed_json.flat_map { |value| json_objects(value) }
    people = objects.count do |object|
      types = Array(object["@type"])
      types.include?("Person")
    end
    contexts = objects.map { |object| object["@context"] }.compact
    errors << "#{relative}: expected one authoritative Person entity, found #{people}" unless people == 1
    errors << "#{relative}: missing HTTPS Schema.org context" unless contexts.include?("https://schema.org")
    errors << "#{relative}: contains an insecure Schema.org context" if contexts.any? { |context| context.to_s.start_with?("http://schema.org") }
  end

  page_base = doc.at_css('link[rel="canonical"]')&.[]("href") || "#{site_origin}/"
  doc.css("a[href], link[href], script[src], img[src]").each do |node|
    attribute = node.key?("href") ? "href" : "src"
    value = node[attribute].to_s.strip
    next if value.empty? || value.start_with?("#", "mailto:", "tel:", "javascript:", "data:")

    begin
      uri = URI.join(page_base, value)
    rescue URI::Error
      errors << "#{relative}: invalid #{attribute} URL #{value.inspect}"
      next
    end
    next unless uri.host.nil? || site_hosts.include?(uri.host.downcase)
    next if local_target_exists?(build_dir, uri.path)

    errors << "#{relative}: broken internal reference #{value.inspect}"
  end
end

core_pages.each do |relative, expected_canonical|
  path = File.join(build_dir, relative)
  unless File.file?(path)
    errors << "Missing core page #{relative}"
    next
  end
  doc = parse_html(path)
  canonical = doc.at_css('link[rel="canonical"]')&.[]("href")
  errors << "#{relative}: canonical is #{canonical.inspect}, expected #{expected_canonical.inspect}" unless canonical == expected_canonical
end

redirect_pages.each do |relative, expected_canonical|
  path = File.join(build_dir, relative)
  unless File.file?(path)
    errors << "Missing legacy redirect #{relative}"
    next
  end
  doc = parse_html(path)
  canonical = doc.at_css('link[rel="canonical"]')&.[]("href")
  robots = doc.at_css('meta[name="robots"]')&.[]("content").to_s.downcase
  errors << "#{relative}: canonical is #{canonical.inspect}, expected #{expected_canonical.inspect}" unless canonical == expected_canonical
  errors << "#{relative}: redirect must be noindex" unless robots.include?("noindex")
end

if errors.empty?
  puts "SEO audit passed (#{html_files.length} HTML files, #{core_pages.length} core pages, #{redirect_pages.length} legacy redirects)."
else
  warn "SEO audit failed with #{errors.length} error(s):"
  errors.each { |error| warn "- #{error}" }
  exit 1
end
