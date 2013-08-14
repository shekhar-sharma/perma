import logging

from linky.forms import user_reg_form, regisrtar_member_form, registrar_form, journal_member_form, journal_member_form_edit, regisrtar_member_form_edit
from linky.models import Registrar, Link
from linky.utils import base

from django.contrib.auth.decorators import login_required
from django.http import  HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib import auth
from django.contrib.auth.models import User, Permission, Group
from django.core.paginator import Paginator
from linky.models import PermaUser


logger = logging.getLogger(__name__)

try:
    from linky.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py: %s', e)


@login_required
def landing(request):
    """ The logged-in user's dashboard. """
    # TODO: do we need this? We were using this, but it's need has
    # vanished since we moved the admin panel to the left column (on all admin pages)

    context = {'user': request.user}

    return render_to_response('user_management/landing.html', context)

@login_required
def manage_members(request):
    """ registry and registrar members can manage journal members (the folks that vest links) """

    if request.user.groups.all()[0].name not in ['registrar_member', 'registry_member']:
        return HttpResponseRedirect(reverse('user_management_landing'))

    context = {'user': request.user, 'registrar_members': list(registrars),
        'this_page': 'users'}
    context.update(csrf(request))

    if request.method == 'POST':

        form = regisrtar_member_form(request.POST, prefix = "a")

        if form.is_valid():
            new_user = form.save()

            new_user.backend='django.contrib.auth.backends.ModelBackend'

            group = Group.objects.get(name='registrar_member')
            group.user_set.add(new_user)

            return HttpResponseRedirect(reverse('user_management_manage_registrar_member'))

        else:
            context.update({'regisrtar_register_form': form,})
    else:
        form = regisrtar_member_form(prefix = "a")
        context.update({'regisrtar_register_form': form,})

    return render_to_response('user_management/manage_registrar_members.html', context)

@login_required
def manage_registrar(request):
    """ Linky admins can manage registrars (libraries) """

    if request.user.groups.all()[0].name not in ['registry_member']:
        return HttpResponseRedirect(reverse('user_management_landing'))

    # TODO: support paging at some point
    registrars = Registrar.objects.all()[:500]

    context = {'user': request.user, 'registrars': list(registrars),
        'this_page': 'users'}
    context.update(csrf(request))

    if request.method == 'POST':

        form = registrar_form(request.POST, prefix = "a")

        if form.is_valid():
            new_user = form.save()

            return HttpResponseRedirect(reverse('user_management_manage_registrar'))

        else:
            context.update({'form': form,})
    else:
        form = registrar_form(prefix = "a")
        context.update({'form': form,})

    return render_to_response('user_management/manage_registrars.html', context)

@login_required
def manage_single_registrar(request, registrar_id):
    """ Linky admins can manage registrars (libraries)
        in this view, we allow for edit/delete"""

    if request.user.groups.all()[0].name not in ['registry_member']:
        return HttpResponseRedirect(reverse('user_management_landing'))

    target_registrar = get_object_or_404(Registrar, id=registrar_id)

    context = {'user': request.user, 'target_registrar': target_registrar,
        'this_page': 'users'}
    context.update(csrf(request))

    if request.method == 'POST':

        form = registrar_form(request.POST, prefix = "a", instance=target_registrar)

        if form.is_valid():
            new_user = form.save()

            return HttpResponseRedirect(reverse('user_management_manage_registrar'))

        else:
            context.update({'form': form,})
    else:
        form = registrar_form(prefix = "a", instance=target_registrar)
        context.update({'form': form,})

    return render_to_response('user_management/manage_single_registrar.html', context)

@login_required
def manage_registrar_member(request):
    """ Linky admins can manage registrar members (librarians) """

    if request.user.groups.all()[0].name not in ['registry_member']:
        return HttpResponseRedirect(reverse('user_management_landing'))

    registrar_members = PermaUser.objects.filter(groups__name='registrar_member', is_active=True)

    context = {'user': request.user, 'registrar_members': list(registrar_members),
        'this_page': 'users'}
    context.update(csrf(request))

    if request.method == 'POST':

        form = regisrtar_member_form(request.POST, prefix = "a")

        if form.is_valid():
            new_user = form.save()

            new_user.backend='django.contrib.auth.backends.ModelBackend'
            
            group = Group.objects.get(name='registrar_member')
            new_user.groups.add(group)

            return HttpResponseRedirect(reverse('user_management_manage_registrar_member'))

        else:
            context.update({'form': form,})
    else:
        form = regisrtar_member_form(prefix = "a")
        context.update({'form': form,})

    return render_to_response('user_management/manage_registrar_members.html', context)

@login_required
def manage_single_registrar_member(request, user_id):
    """ Linky admins can manage registrar members (librarians)
        in this view, we allow for edit"""

    if request.user.groups.all()[0].name not in ['registry_member']:
        return HttpResponseRedirect(reverse('user_management_landing'))

    target_registrar_member = get_object_or_404(PermaUser, id=user_id)

    context = {'user': request.user, 'target_registrar_member': target_registrar_member,
        'this_page': 'users'}
    context.update(csrf(request))

    if request.method == 'POST':

        form = regisrtar_member_form_edit(request.POST, prefix = "a", instance=target_registrar_member)

        if form.is_valid():
            new_user = form.save()

            return HttpResponseRedirect(reverse('user_management_manage_registrar_member'))

        else:
            context.update({'form': form,})
    else:
        form = regisrtar_member_form_edit(prefix = "a", instance=target_registrar_member)
        context.update({'form': form,})

    return render_to_response('user_management/manage_single_registrar_member.html', context)

@login_required
def manage_single_registrar_member_delete(request, user_id):
    """ Linky admins can manage registrar members. Delete a single registrar member here. """

    # Only registry members can delete registrar members
    if request.user.groups.all()[0].name not in ['registry_member']:
        return HttpResponseRedirect(reverse('user_management_landing'))

    target_member = get_object_or_404(User, id=user_id)

    context = {'user': request.user, 'target_member': target_member,
        'this_page': 'users'}
    context.update(csrf(request))

    if request.method == 'POST':
        target_member.is_active = False
        target_member.save()

        return HttpResponseRedirect(reverse('user_management_manage_registrar_member'))
    else:
        form = journal_member_form_edit(prefix = "a", instance=target_member)
        context.update({'form': form,})

    return render_to_response('user_management/manage_single_registrar_member_delete_confirm.html', context)

@login_required
def manage_journal_member(request):
    """ Linky admins and registrars can manage journal members """

    if request.user.groups.all()[0].name not in ['registrar_member', 'registry_member']:
        return HttpResponseRedirect(reverse('user_management_landing'))

    # If registry member, return all active journal members. If registrar member, return just those journal members that belong to the registrar member's registrar
    if request.user.groups.all()[0].name == 'registry_member':
        journal_members = PermaUser.objects.filter(groups__name='journal_member', is_active=True)
    else:
        journal_members = PermaUser.objects.filter(registrar=request.user.registrar, is_active=True).exclude(id=request.user.id)

    context = {'user': request.user, 'journal_members': list(journal_members),
        'this_page': 'users'}
    context.update(csrf(request))

    if request.method == 'POST':

        form = journal_member_form(request.POST, prefix = "a")

        if form.is_valid():
            new_user = form.save()

            new_user.backend='django.contrib.auth.backends.ModelBackend'
            
            new_user.registrar = request.user.registrar
            logger.debug('Trying to save with registrar: %s', request.user.registrar)
            new_user.save()

            group = Group.objects.get(name='journal_member')
            new_user.groups.add(group)

            return HttpResponseRedirect(reverse('user_management_manage_journal_member'))

        else:
            context.update({'form': form,})
    else:
        form = journal_member_form(prefix = "a")
        context.update({'form': form,})

    return render_to_response('user_management/manage_journal_members.html', context)

@login_required
def manage_single_journal_member(request, user_id):
    """ Linky admins and registrars can manage journal members. Edit a single journal member here. """

    # Only registry members and registrar memebers can edit journal members
    if request.user.groups.all()[0].name not in ['registrar_member', 'registry_member']:
        return HttpResponseRedirect(reverse('user_management_landing'))

    target_member = get_object_or_404(PermaUser, id=user_id)

    # Registrar members can only edit their own journal members
    if request.user.groups.all()[0].name not in ['registry_member']:
        if request.user.registrar != target_member.registrar:
            return HttpResponseRedirect(reverse('user_management_landing'))


    context = {'user': request.user, 'target_member': target_member,
        'this_page': 'users'}
    context.update(csrf(request))

    if request.method == 'POST':

        form = journal_member_form_edit(request.POST, prefix = "a", instance=target_member)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('user_management_manage_journal_member'))

        else:
            context.update({'form': form,})
    else:
        form = journal_member_form_edit(prefix = "a", instance=target_member)
        context.update({'form': form,})

    return render_to_response('user_management/manage_single_journal_member.html', context)

@login_required
def manage_single_journal_member_delete(request, user_id):
    """ Linky admins and registrars can manage journal members. Delete a single journal member here. """

    # Only registry members and registrar memebers can edit journal members
    if request.user.groups.all()[0].name not in ['registrar_member', 'registry_member']:
        return HttpResponseRedirect(reverse('user_management_landing'))

    target_member = get_object_or_404(User, id=user_id)

    # Registrar members can only edit their own journal members
    if request.user.groups.all()[0].name not in ['registry_member']:
        if request.user.get_profile().registrar != target_member.get_profile().registrar:
            return HttpResponseRedirect(reverse('user_management_landing'))

    context = {'user': request.user, 'target_member': target_member,
        'this_page': 'users'}
    context.update(csrf(request))

    if request.method == 'POST':
        target_member.is_active = False
        target_member.save()

        return HttpResponseRedirect(reverse('user_management_manage_journal_member'))
    else:
        form = journal_member_form_edit(prefix = "a", instance=target_member)
        context.update({'form': form,})

    return render_to_response('user_management/manage_single_journal_member_delete_confirm.html', context)

valid_sorts = ['-creation_timestamp', 'creation_timestamp', 'vested_timestamp', '-vested_timestamp']

@login_required
def created_links(request):
    """ Anyone with an account can view the linky links they've created """

    DEFAULT_SORT = '-creation_timestamp'

    sort = request.GET.get('sort', DEFAULT_SORT)
    if sort not in valid_sorts:
        sort = DEFAULT_SORT
    page = request.GET.get('page', 1)
    if page < 1:
        page = 1

    linky_links = Link.objects.filter(created_by=request.user).order_by(sort)
    total_created = len(linky_links)

    paginator = Paginator(linky_links, 10)
    linky_links = paginator.page(page)

    for linky_link in linky_links:
        #linky_link.id =  base.convert(linky_link.id, base.BASE10, base.BASE58)
        if len(linky_link.submitted_title) > 50:
          linky_link.submitted_title = linky_link.submitted_title[:50] + '...'
        if len(linky_link.submitted_url) > 79:
          linky_link.submitted_url = linky_link.submitted_url[:70] + '...'

    context = {'user': request.user, 'linky_links': linky_links, 'host': request.get_host(),
               'total_created': total_created, sort : sort, 'this_page': 'created_links'}

    return render_to_response('user_management/created-links.html', context)

@login_required
def vested_links(request):
    """ Linky admins and registrar members and journal members can vest link links """

    if request.user.groups.all()[0].name not in ['journal_member', 'registrar_member', 'registry_member']:
        return HttpResponseRedirect(reverse('user_management_landing'))
        
    
    DEFAULT_SORT = '-creation_timestamp'

    sort = request.GET.get('sort', DEFAULT_SORT)
    if sort not in valid_sorts:
        sort = DEFAULT_SORT
    page = request.GET.get('page', 1)
    if page < 1:
        page = 1

    linky_links = Link.objects.filter(vested_by_editor=request.user).order_by(sort)
    total_vested = len(linky_links)
    
    paginator = Paginator(linky_links, 10)
    linky_links = paginator.page(page)

    for linky_link in linky_links:
        #linky_link.id =  base.convert(linky_link.id, base.BASE10, base.BASE58)
        if len(linky_link.submitted_title) > 50:
          linky_link.submitted_title = linky_link.submitted_title[:50] + '...'
        if len(linky_link.submitted_url) > 79:
          linky_link.submitted_url = linky_link.submitted_url[:70] + '...'

    context = {'user': request.user, 'linky_links': linky_links, 'host': request.get_host(),
               'total_vested': total_vested, 'this_page': 'vested_links'}

    return render_to_response('user_management/vested-links.html', context)

@login_required
def manage_account(request):
    """ Account mangement stuff. Change password, change email, ... """

    context = {'host': request.get_host(), 'user': request.user,
        'next': request.get_full_path(), 'this_page': 'settings'}
    context.update(csrf(request))

    return render_to_response('user_management/manage-account.html', context)

@login_required
def batch_convert(request):
    """Detect and archive URLs from user input."""
    # TODO
    context = {'host': request.get_host(), 'user': request.user,
        'this_page': 'batch_convert'}
    context.update(csrf(request))
    return render_to_response('user_management/batch_convert.html', context)

@login_required
def export(request):
    """Export a CSV of a user's library."""
    # TODO
    context = {'host': request.get_host(), 'user': request.user,
        'this_page': 'export'}
    context.update(csrf(request))
    return render_to_response('user_management/export.html', context)

@login_required
def custom_domain(request):
    """Instructions for a user to configure a custom domain."""
    # TODO
    context = {'host': request.get_host(), 'user': request.user,
        'this_page': 'custom_domain'}
    context.update(csrf(request))
    return render_to_response('user_management/custom_domain.html', context)

@login_required
def sponsoring_library(request):
    """ Journal members can view their sponsoring library (for contact info) """

    

    context = {'user': request.user, 'sponsoring_library_name': request.user.registrar.name, 'sponsoring_library_email': request.user.registrar.email, 'sponsoring_library_website': request.user.registrar.website}

    return render_to_response('user_management/sponsoring-library.html', context)

def process_register(request):
    """Register a new user"""
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':

        reg_key = request.POST.get('reg_key', '')

        editor_reg_form = user_reg_form(request.POST, prefix = "a")

        if editor_reg_form.is_valid():
            new_user = editor_reg_form.save()

            new_user.backend='django.contrib.auth.backends.ModelBackend'

            group = Group.objects.get(name='user')
            group.user_set.add(new_user)

            return HttpResponseRedirect(reverse('landing'))

        else:
            c.update({'editor_reg_form': editor_reg_form,})

            return render_to_response('registration/register.html', c)
    else:
        editor_reg_form = user_reg_form (prefix = "a")

        c.update({'editor_reg_form': editor_reg_form,})
        return render_to_response("registration/register.html", c)
