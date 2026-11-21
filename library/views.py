from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Avg

from .models import Article, ArticleComment, ArticleRating
from .forms import ArticleForm, ArticleCommentForm
from profiles.models import Hobby
from notifications.services import NotificationDispatcher
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'library/article_list.html'
    context_object_name = 'articles'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        hobby_slug = self.request.GET.get('hobby')
        if hobby_slug:
            queryset = queryset.filter(hobby__slug=hobby_slug)
        
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(title__icontains=q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hobbies'] = Hobby.objects.filter(articles__isnull=False).distinct()
        return context

class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    template_name = 'library/article_detail.html'
    context_object_name = 'article'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = ArticleCommentForm()
        
        ratings = self.object.ratings.all()
        if ratings.exists():
            context['average_rating'] = ratings.aggregate(Avg('rating'))['rating__avg']
            context['total_ratings'] = ratings.count()
        else:
            context['average_rating'] = None
            context['total_ratings'] = 0
            
        if self.request.user.is_authenticated:
            context['user_rating'] = ratings.filter(author=self.request.user).first()
            
        return context

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'library/article_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Artículo publicado con éxito.")
        return super().form_valid(form)

class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'library/article_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
    
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.is_superuser
        
    def form_valid(self, form):
        messages.success(self.request, "Artículo actualizado con éxito.")
        return super().form_valid(form)

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    template_name = 'library/article_confirm_delete.html'
    success_url = reverse_lazy('library:article_list')
    
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.is_superuser
        
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Artículo eliminado con éxito.")
        return super().delete(request, *args, **kwargs)

@login_required
@require_POST
def add_comment(request, slug):
    article = get_object_or_404(Article, slug=slug)
    form = ArticleCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.author = request.user
        comment.save()
        
        if article.author != request.user:
            action_url = request.build_absolute_uri(
                reverse('library:article_detail', kwargs={'slug': slug})
            )
            NotificationDispatcher.dispatch(
                notification_type='article_comment',
                sender=request.user,
                recipient=article.author,
                article=article,
                message=f'ha comentado en tu artículo "{article.title}"',
                send_email=True,
                email_subject=f'💬 Nuevo comentario en tu artículo: {article.title}',
                email_body=f'¡Hola {article.author.username}!\n\n@{request.user.username} ha dejado un comentario en tu artículo "{article.title}".',
                action_url=action_url,
            )
        messages.success(request, "Comentario añadido.")
    return redirect('library:article_detail', slug=slug)

@login_required
@require_POST
def rate_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    rating_val = request.POST.get('rating')
    if rating_val and rating_val.isdigit() and 1 <= int(rating_val) <= 5:
        rating, created = ArticleRating.objects.update_or_create(
            article=article,
            author=request.user,
            defaults={'rating': int(rating_val)}
        )
        if created and article.author != request.user:
            action_url = request.build_absolute_uri(
                reverse('library:article_detail', kwargs={'slug': slug})
            )
            NotificationDispatcher.dispatch(
                notification_type='article_rating',
                sender=request.user,
                recipient=article.author,
                article=article,
                message=f'ha valorado tu artículo "{article.title}" con {rating_val} estrellas',
                send_email=True,
                email_subject=f'⭐ Nueva valoración en tu artículo: {article.title}',
                email_body=f'¡Hola {article.author.username}!\n\n@{request.user.username} ha valorado tu artículo "{article.title}" con {rating_val} estrellas.',
                action_url=action_url,
            )
        messages.success(request, "Valoración guardada.")
    return redirect('library:article_detail', slug=slug)
