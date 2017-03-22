from django.contrib.sessions.models import Session
from .models import MySession, Comment, Thread
from django.core.exceptions import ObjectDoesNotExist
import re


def create_mysession_in_board(request, name_board):
    """
    Считаем сессии для подсчета пользователей на доске
    """
    request.session.set_expiry(3600)
    request.session.save()

    session_key = request.session.session_key
    if len(MySession.objects.filter(session_key=session_key)) != 0:
        session = MySession.objects.get(session_key=session_key)
        if name_board in session.name_board:
            pass
        else:
            session.name_board += ', ' + name_board
            session.save()
    else:
        MySession.objects.create(session_key=Session.objects.get(pk=session_key), name_board=name_board,
                                 expire_date=Session.objects.get(pk=session_key).expire_date)


def set_active_user_in_board(request, name_board):
    """
    Считаем сессии для подсчета активных пользователей на доске
    """
    try:
        session = MySession.objects.get(session_key=request.session.session_key)
    except ObjectDoesNotExist:
        return None
    if name_board in session.active:
        pass
    elif session.active == '':
        session.active = name_board
    else:
        session.active += ', ' + name_board
    request.session.set_expiry(86400)
    session.expire_date = Session.objects.get(pk=request.session.session_key).expire_date
    session.save()


def create_mysession_in_thread(request, name_board, pk):
    """
    Считаем количество пользователей на доске + считаем количество посетивших тред для score
    """
    request.session.set_expiry(3600)
    request.session.save()

    session_key = request.session.session_key
    if len(MySession.objects.filter(session_key=session_key)) != 0:
        session = MySession.objects.get(session_key=session_key)
        if name_board in session.name_board:
            pass
        else:
            session.name_board += ', ' + name_board
        if pk in session.thread:
            pass
        elif session.thread == '':
            session.thread = pk
        else:
            session.thread += ', ' + pk
        session.save()
    else:
        MySession.objects.create(session_key=Session.objects.get(pk=session_key), name_board=name_board,
                                 expire_date=Session.objects.get(pk=session_key).expire_date, thread=pk)


def set_active_user_in_thread(request, name_board):
    """
    Считаем количество активных пользователей на доске
    """
    try:
        session = MySession.objects.get(session_key=request.session.session_key)
    except ObjectDoesNotExist:
        return None

    if name_board in session.active:
        pass
    elif session.active == '':
        session.active = name_board
    else:
        session.active += ', ' + name_board

    request.session.set_expiry(86400)
    session.expire_date = Session.objects.get(pk=request.session.session_key).expire_date
    session.save()


def search_patterns(answers, comment, reg):
    """
    Если были использованы ответы по id, то выделяем их тэгами cсылки
    """
    counter_pattern = 0
    for x in re.finditer(reg, comment.comments_text):
        counter_pattern += 1
    count_pattern = counter_pattern
    count_tagged_pattern = 0
    while counter_pattern != 0:
        iter_pattern = re.finditer(reg, comment.comments_text)
        k = 0
        for x in iter_pattern:
            if count_tagged_pattern == count_pattern - counter_pattern:
                if x.span()[0] == 0 and count_tagged_pattern == 0:
                    answers.append(comment.comments_text[2:x.span()[1]])
                    if reg == re.compile('>>[\d]+(?! \(OP\)|\w)'):
                        comment.comments_text = '<a class="link-reply" data-num="%s">' % (
                            comment.comments_text[2:x.span()[1]] + ' comment') + comment.comments_text[:x.span()[1]] +\
                                                '</a>' + comment.comments_text[x.span()[1]:]
                    else:
                        comment.comments_text = '<a class="link-reply" data-num="%s">' % (
                            comment.comments_text[2:x.span()[1] - 5] + ' thread') +\
                                                comment.comments_text[:x.span()[1]] + '</a>' +\
                                                comment.comments_text[x.span()[1]:]
                    break
                else:
                    if k == count_pattern - counter_pattern:
                        answers.append(comment.comments_text[x.span()[0] + 2:x.span()[1]])
                        if reg == re.compile('>>[\d]+(?! \(OP\)|\w)'):
                            comment.comments_text = comment.comments_text[
                                                    :x.span()[0]] + '<a class="link-reply" data-num="%s">' % (
                                comment.comments_text[x.span()[0] + 2:x.span()[1]] + ' comment') + \
                                                    comment.comments_text[x.span()[0]:x.span()[1]] + '</a>' + \
                                                    comment.comments_text[x.span()[1]:]
                        else:
                            comment.comments_text = comment.comments_text[
                                                    :x.span()[0]] + '<a class="link-reply" data-num="%s">' % (
                                comment.comments_text[x.span()[0] + 2:x.span()[1] - 5] + ' thread') + \
                                                    comment.comments_text[x.span()[0]:x.span()[1]] + '</a>' + \
                                                    comment.comments_text[x.span()[1]:]
                        break
            k += 1
        count_tagged_pattern += 1
        counter_pattern -= 1


def add_answers(reg, comment, answers):
    """
    Если были использованы ответы по id, то добавляем в бд к какому-то посту был какой ответ
    """
    for x in answers:
        if reg == re.compile('>>[\d]+(?! \(OP\)|\w)'):
            comment_for_answers = Comment.objects.get(pk=x)
            if comment_for_answers.comments_answers == '':
                comment_for_answers.comments_answers = str(comment.id)
            else:
                comment_for_answers.comments_answers += ',' + str(comment.id)
            comment_for_answers.save()
        else:
            result = re.search(r'[\d]+', x)
            x = result.group(0)
            thread_for_answers = Thread.objects.get(pk=x)
            if thread_for_answers.thread_answers == '':
                thread_for_answers.thread_answers = str(comment.id)
            else:
                thread_for_answers.thread_answers += ',' + str(comment.id)
            thread_for_answers.save()
