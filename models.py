from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=120, blank=False, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name


class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    category = models.ForeignKey(Category, null=True)
    title = models.CharField(max_length=120, blank=False)
    slug = models.SlugField(unique=True)
    content = models.TextField(blank=False)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    published_at = models.DateTimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'slug': self.slug})

    class Meta:
        ordering = ["-created_at", "-updated_at"]


def create_slug(instance, new_slug=None):
    slug = new_slug

    if slug is None:
        slug = slugify(instance.title)

    qs = Article.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = '{0}-{1}'.format(slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)

    return slug


def pre_save_article_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_article_receiver, sender=Article)
