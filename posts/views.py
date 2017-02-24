from django.contrib import messages
from django.contrib.contenttypes.models import ContentType  
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Post
from .form import PostForm 
from .utils import count_words, get_read_time

from comments.models import Comment 
from comments.form import CommentForm

# Create your views here.


def posts_home(request):
    return HttpResponse("<h1>Hello World</h1>")

def posts_list(request):
    queryset = Post.objects.all()
    query = request.GET.get('query')
    if query is not None:
        queryset = queryset.filter(title__icontains=query)
    paginator = Paginator(queryset, 6) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    context = {
        'title' : 'List',
        'contacts': contacts
    }
    return render(request, 'post_list.html', context)

"""
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

def listing(request):
    contact_list = Contacts.objects.all()
    paginator = Paginator(contact_list, 25) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    return render(request, 'list.html', {'contacts': contacts})
"""
def posts_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    # if not request.user.is_authenticated():
    #     raise Http404
    form = PostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.success(request, "Successful Post Created.")
            return HttpResponseRedirect(instance.get_absolute_url())
        else:
            messages.warning(request, "Please correct below error")
    context = {
        'form': form
    }
    return render(request, 'post_form.html', context)

def posts_detail(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    # content_type = ContentType.objects.get_for_model(Post)
    # object_id = instance.id
    # comments = Comment.objects.filter(content_type=content_type, object_id=object_id)
    initial_data = {
        'content_type': instance.get_content_type,
        'object_id': instance.id,
    }
    comment_form = CommentForm(request.POST or None, initial=initial_data)
    if comment_form.is_valid():
        c_type = comment_form.cleaned_data.get('content_type')
        content_type = ContentType.objects.get(model=c_type)
        object_id = comment_form.cleaned_data.get('object_id')
        content_data = comment_form.cleaned_data.get('content')

        parent_obj = None 
        try:
            parent_id = int(request.POST.get('parent_id'))
        except:
            parent_id = None
        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()

        new_comment, created = Comment.objects.get_or_create(
                                               user= request.user,
                                               content_type= content_type,
                                               object_id=object_id,
                                               content=content_data,
                                               parent=parent_obj)
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    comments = instance.comments
    context = {
        'title' : 'Detail',
        'object': instance,
        'comments': comments,
        'comment_form': comment_form,
        'words_count': count_words(instance.get_markdown()),
        'read_time': get_read_time(instance.get_markdown()),
    }
    return render(request, 'post_detail.html', context)

def posts_update(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.error(request, "Successful Post Updated.")
        return HttpResponseRedirect(instance.get_absolute_url())
    else:
        messages.warning(request, "Please correct below error")
    context = {
        'form': form
    }
    return render(request, 'post_form.html', context)

def posts_delete(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    instance.delete()
    messages.success(request, "Successful delete.")
    return redirect("list")
