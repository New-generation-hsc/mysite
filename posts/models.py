from django.db import models
from django.db.models.signals import pre_save
from django.core.urlresolvers import reverse

from django.utils.text import slugify
from django.utils.safestring import mark_safe
from django.utils import timezone 

from django.contrib.contenttypes.models import ContentType  
from django.conf import settings

from markdown_deux import markdown
from comments.models import Comment
# Create your models here.

def upload_location(instance, filename):
    return "images/%s" % filename

class PostManager(models.Manager):
    def all(self, *args, **kwargs):
        return super(PostManager, self).filter(publish__lte=timezone.now())


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, null=True, blank=True)
    image =  models.ImageField(upload_to=upload_location,
                               null=True, blank=True,
                               height_field="height_field",
                               width_field="width_field")
    height_field = models.IntegerField(default=0)
    width_field = models.IntegerField(default=0)
    content = models.TextField()
    draft = models.BooleanField(default=False)
    publish = models.DateField(auto_now=False, auto_now_add=False)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    post = PostManager()
    objects = models.Manager()

    class Meta:
        ordering = ['title', 'updated']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        #return "/posts/detail/%s/" % self.id
        return reverse('detail', kwargs={'slug' : self.slug})

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

    @property 
    def comments(self):
        instance = self 
        qs = Comment.objects.filter_by_instance(instance)
        return qs

    @property 
    def get_content_type(self):
        instance = self 
        content_type = ContentType.objects.get_for_model(instance.__class__)
        return content_type


def create_slug(instance, new_slug=None):
    slug = slugify(instance.title)
    if new_slug is not None:
        slug = new_slug
    queryset = Post.objects.filter(slug=slug).order_by("-id")
    exists = queryset.exists()
    if exists:
        new_slug = "%s-%s" % (slug, queryset.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, sender=Post)
