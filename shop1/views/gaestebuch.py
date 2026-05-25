"""Gästebuch und Kommentare."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Comment
from ._helpers import _is_admin


def gaestebuch(request):
    """Zeigt alle Haupt-Kommentare und deren Antworten an."""
    comments = (
        Comment.objects
        .filter(parent=None)
        .select_related('user')
        .prefetch_related('replies', 'likes')
        .order_by('-erstellt_am')
    )
    return render(request, 'shop1/gaestebuch.html', {'comments': comments})


@login_required(login_url='login')
def comment_add(request):
    """Fügt einen neuen Kommentar oder eine Antwort hinzu."""
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        parent_id = request.POST.get('parent_id')

        if not text:
            messages.error(request, 'Bitte gib eine Nachricht ein.')
            return redirect('gaestebuch')

        if len(text) > 2000:
            messages.error(request, 'Nachricht ist zu lang (max. 2000 Zeichen).')
            return redirect('gaestebuch')

        parent = None
        is_admin_reply = False
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)
            if _is_admin(request.user):
                is_admin_reply = True

        Comment.objects.create(
            user=request.user,
            text=text,
            parent=parent,
            is_admin_reply=is_admin_reply,
        )
        messages.success(request, 'Dein Beitrag wurde im Orbit veröffentlicht!')
    return redirect('gaestebuch')


@login_required(login_url='login')
def comment_like(request, comment_id):
    """Liked oder ent-liked einen Kommentar."""
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
    else:
        comment.likes.add(request.user)
    return redirect('gaestebuch')


@login_required(login_url='login')
def comment_delete(request, comment_id):
    """Löscht einen Kommentar (nur Admin oder Ersteller)."""
    comment = get_object_or_404(Comment, id=comment_id)
    if _is_admin(request.user) or comment.user == request.user:
        comment.delete()
        messages.success(request, 'Beitrag wurde gelöscht.')
    else:
        messages.error(request, 'Keine Berechtigung zum Löschen.')
    return redirect('gaestebuch')
