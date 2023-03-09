import scrapy
from googletrans import Translator

class webScrapingSpider(scrapy.Spider):
    name = 'webScraping'
    allowed_domains = ['classcentral.com']
    start_urls = ['http://classcentral.com/subjects']

    def __init__(self, subject=None):
        self.subject = subject
        self.translator = Translator(service_urls=['translate.google.com'])
        
    def parse(self,response):
                # Translate the response body to Hindi
        response_text = response.text
        translated_text = self.translator.translate(response_text, dest='hi').text
        response = response.replace(body=translated_text)
        
        subjects = response.css('.text-1.color-charcoal.weight-bold::text').extract()
        paths = response.xpath('//*[@class="border-box align-middle padding-right-xsmall"]/@href').extract()
        urls = ['https://classcentral.com' + path for path in paths] 
        categorys = dict(zip(subjects,urls))

        if self.subject:
            if self.subject in categorys:
                url = categorys[self.subject]
                yield scrapy.Request(url,callback=self.parse_urls)
        else:
            for url in urls:
                yield scrapy.Request(url,callback=self.parse_urls)

    def parse_urls(self,response):
        subject = response.css('h1::text').extract_first()
        courses = response.xpath('//tr[@itemtype="http://schema.org/Event"]')
        for course in courses:
            course_name = course.xpath('.//*[@itemprop="name"]/text()').extract_first().strip()
            course_url = 'https://classcentral.com' + course.xpath('.//a[@class="color-charcoal block line-tight course-name"]/@href').extract_first()
            institution = course.xpath('.//a[@class="color-charcoal small-down-text-2 text-3"]/text()').extract_first().strip()
            duration = course.xpath('.//span[@class="hidden medium-up-inline-block small-down-text-2 text-3  large-up-margin-left-xxsmall  icon-clock-charcoal icon-left-small"]/text()').extract_first().strip().replace('          ','').replace('\n','')
            provider = course.xpath('.//a[@class="color-charcoal italic"]/text()').extract_first().replace('\n','').strip()
            yield{
                'Subject':self.translator.translate(subject, dest='hi').text,
                'Institution': self.translator.translate(institution, dest='hi').text,
                'Course Name':self.translator.translate(course_name, dest='hi').text,
                'Course Url':course_url,
                'Duration':self.translator.translate(duration, dest='hi').text,
                'Provider':self.translator.translate(provider, dest='hi').text
            }
        next_page = response.xpath('//link[@rel="next"]/@href').extract_first()
        if next_page:
            absolute_next_page = response.urljoin(next_page)
            yield Request(absolute_next_page,callback=self.parse_urls)