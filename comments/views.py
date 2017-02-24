from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404, HttpResponse
from .models import Comment 
from .form import CommentForm

# Create your views here.
@login_required(login_url='/login/')
def comment_delete(request, id):
    obj = get_object_or_404(Comment, id=id)

    if obj.user != request.user:
        reponse = HttpResponse()
        reponse.status_code = 403
        return reponse
    
    if request.method == 'POST':
        parent_obj_url = obj.content_object.get_absolute_url()
        obj.delete()
        messages.success(request, "You successfully delete that comment.")
        return HttpResponseRedirect(parent_obj_url)
    context = {
        'comment': obj
    }
    return render(request, 'comfirm_delete.html', context)

def comment_thread(request, id):
    instance = get_object_or_404(Comment, id=id)
	#instance is class Comment
    content_type = instance.content_type
    object_id = instance.object_id

    initial_data = {
        'content_type': content_type,
        'object_id': object_id,
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
        return HttpResponseRedirect(new_comment.content_type.get_absolute_url())
    context = {
        'comment_form': comment_form,
    	'comment': instance,
    } 
    return render(request, "comment_thread.html", context)