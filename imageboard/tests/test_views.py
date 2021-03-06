from django.test import TestCase
from django.urls import reverse

from imageboard.forms import NewCommentForm, NewThreadForm
from imageboard.models import Board, Comment, MySession, Thread


class ViewIndex(TestCase):
    fixtures = ['Imageboard.json']

    def test_smoke(self):
        response = self.client.get(reverse('index'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class ViewContacts(TestCase):
    fixtures = ['Imageboard.json']

    def test_smoke(self):
        response = self.client.get(reverse('contacts'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contacts.html')


class ViewThreadList(TestCase):
    fixtures = ['Imageboard.json']

    def test_smoke(self):
        response = self.client.get(reverse('board', kwargs={'name_board': 'b'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board.html')

    def test_board_not_exists(self):
        response = self.client.get(reverse('board', kwargs={'name_board': 'zz'}))

        self.assertEqual(response.status_code, 404)

    def test_len_thread(self):
        response = self.client.get(reverse('board', kwargs={'name_board': 'b'}))

        self.assertEqual(len(response.context['threads']), 2)

    def test_len_threads(self):
        for x in range(1, 6):
            Thread.objects.create(
                board=Board.objects.get(board_shortcut='b'),
                thread_text='sdfsdf',
            )
        response = self.client.get(reverse('board', kwargs={'name_board': 'b'}))

        self.assertEqual(len(response.context['threads']), 5)

    def test_context(self):
        response = self.client.get(reverse('board', kwargs={'name_board': 'b'}))
        form_thread = NewThreadForm()
        form_comment = NewCommentForm()
        board = Board.objects.get(board_shortcut='b')

        self.assertEqual(str(response.context['form_thread']), str(form_thread))
        self.assertEqual(str(response.context['form_comment']), str(form_comment))
        self.assertEqual(response.context['name_board'], 'b')
        self.assertEqual(response.context['board'], board)

    def test_smoke_ajax(self):
        response = self.client.get(reverse('board', kwargs={'name_board': 'b'}), {'value': '5'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)

    def test_ajax_threads(self):
        for x in range(1, 11):
            Thread.objects.create(
                board=Board.objects.get(board_shortcut='b'),
                thread_text='sdfsdfsdf',
            )
        response = self.client.get(reverse('board', kwargs={'name_board': 'b'}), {'value': '5'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(len(response.json()), 5)

    def test_ajax_comments_less_three(self):
        for x in range(1, 6):
            thread = Thread.objects.create(
                board=Board.objects.get(board_shortcut='b'),
                thread_text='sdfsdfsdf',
            )
            Comment.objects.create(
                thread=thread,
                comments_text='sdfsdfsd',
            )
        response = self.client.get(reverse('board', kwargs={'name_board': 'b'}), {'value': '5'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(len(response.json()), 4)

    def test_ajax_comments_over_three(self):
        for x in range(1, 6):
            thread = Thread.objects.create(
                board=Board.objects.get(board_shortcut='b'),
                thread_text='sdfsdfsdf',
            )
            for y in range(1, 5):
                Comment.objects.create(
                    thread=thread,
                    comments_text='sdfsdfsd',
                )
        response = self.client.get(reverse('board', kwargs={'name_board': 'b'}), {'value': '5'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(len(response.json()), 8)

    def test_create_mysession_one_board(self):
        session = self.client.session.session_key
        self.client.get(reverse('board', kwargs={'name_board': 'b'}))
        mysession = MySession.objects.get(session_key=session)

        self.assertEqual(mysession.name_board, 'b')

        self.client.get(reverse('board', kwargs={'name_board': 'b'}))

        self.assertEqual(mysession.name_board, 'b')

    def test_create_mysession_more_board(self):
        session = self.client.session.session_key
        self.client.get(reverse('board', kwargs={'name_board': 'b'}))
        self.client.get(reverse('board', kwargs={'name_board': 'pr'}))
        mysession = MySession.objects.get(session_key=session)

        self.assertEqual(mysession.name_board, 'b, pr')


class ViewDetailThread(TestCase):
    fixtures = ['Imageboard.json']

    def test_smoke(self):
        response = self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': '1'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'thread.html')

    def test_context(self):
        response = self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': '1'}))

        self.assertEqual(str(response.context['comments']), str(Comment.objects.filter(thread__id=1)
                                                                .order_by('comments_time')))
        self.assertEqual(response.context['name_board'], 'b')
        self.assertEqual(response.context['board'], Board.objects.get(board_shortcut='b'))
        self.assertEqual(str(response.context['form']), str(NewCommentForm()))
        self.assertEqual(response.context['pk'], str(1))

    def test_create_mysession_one_board(self):
        session = self.client.session.session_key
        self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': '1'}))
        mysession = MySession.objects.get(session_key=session)

        self.assertEqual(mysession.name_board, 'b')

        self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': '1'}))

        self.assertEqual(mysession.name_board, 'b')
        self.assertEqual(mysession.thread, '1')

    def test_create_mysession_more_board(self):
        session = self.client.session.session_key
        self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': '1'}))
        self.client.get(reverse('thread', kwargs={'name_board': 'pr', 'pk': '2'}))
        mysession = MySession.objects.get(session_key=session)

        self.assertEqual(mysession.name_board, 'b, pr')
        self.assertEqual(mysession.thread, '1, 2')

        self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': '1'}))

        self.assertEqual(mysession.thread, '1, 2')


class ViewFormAddThread(TestCase):
    fixtures = ['Imageboard.json']

    def test_smoke(self):
        response = self.client.post(reverse('AddThread', kwargs={'name_board': 'b'}), {'thread_text': 'thsdnasf'})

        self.assertEqual(response.status_code, 302)

    def test_form(self):
        response = self.client.post(reverse('AddThread', kwargs={'name_board': 'b'}), {'thread_text': 'thsdnasf'})
        response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)

    def test_set_active_user_one_thread(self):
        session = self.client.session.session_key
        self.client.get(reverse('board', kwargs={'name_board': 'b'}))
        self.client.post(reverse('AddThread', kwargs={'name_board': 'b'}), {'thread_text': 'sdfsdfsdf'})
        mysession = MySession.objects.get(session_key=session)

        self.assertEqual(mysession.active, 'b')

        self.client.post(reverse('AddThread', kwargs={'name_board': 'b'}), {'thread_text': 'sdfsdrer'})

        self.assertEqual(mysession.active, 'b')

    def test_set_active_user_more_thread(self):
        session = self.client.session.session_key
        self.client.get(reverse('board', kwargs={'name_board': 'b'}))
        self.client.post(reverse('AddThread', kwargs={'name_board': 'b'}), {'thread_text': 'sdfsdfsdf'})
        self.client.get(reverse('board', kwargs={'name_board': 'pr'}))
        self.client.post(reverse('AddThread', kwargs={'name_board': 'pr'}), {'thread_text': 'aasdasdas'})
        mysession = MySession.objects.get(session_key=session)

        self.assertEqual(mysession.active, 'b, pr')


class ViewAddComment(TestCase):
    fixtures = ['Imageboard.json']

    def test_smoke(self):
        response = self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text':
                                                                                                 'sdfsdfsdf'})

        self.assertEqual(response.status_code, 302)

    def test_add_comment(self):
        response = self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': 1}))
        comments = len(response.context['comments'])
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text': 'sdfsdfsdf'})
        response = self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': 1}))

        self.assertEqual(len(response.context['comments']), comments + 1)

    def test_text_processing_1(self):
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text':
                                                                                      '>>1 (OP) sdfsdf'})
        response = self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': 1}))

        self.assertIn('<a class="link-reply" data-num="1 thread">>>1 (OP)</a>', str(response.content))

    def test_text_processing_2(self):
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text': '>>1 sdfsdfsf'})
        response = self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': 1}))

        self.assertIn('<a class="link-reply" data-num="1 comment">>>1</a>', str(response.content))

    def test_text_processing_3(self):
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text':
                                                                                      '>>1 (OP) sdfsdfsf  >>1'})
        response = self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': 1}))

        self.assertIn('<a class="link-reply" data-num="1 thread">>>1 (OP)</a>', str(response.content))
        self.assertIn('<a class="link-reply" data-num="1 comment">>>1</a>', str(response.content))

    def test_answer_for_comments(self):
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text': 'sdfsdfsf  >>2'})
        answers = Comment.objects.get(id=2).comments_answers

        self.assertIn(str(5), answers)

    def test_answer_for_threads(self):
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text':
                                                                                      'sdfsdfsf  >>1 (OP)'})
        answers = Thread.objects.get(id=1).thread_answers

        self.assertIn(str(1), answers)

    def test_answers_for_comments(self):
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text': 'sdfsdfsf  >>2'})
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text': 'sdfsewtr  >>2'})
        answers = Comment.objects.get(id=2).comments_answers

        self.assertIn((str(7) + ',' + str(8)), answers)

    def test_answers_for_threads(self):
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text':
                                                                                      'sdfsdfsf  >>1 (OP)'})
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text':
                                                                                      'ssdf423s  >>1 (OP)'})
        answers = Thread.objects.get(id=1).thread_answers

        self.assertIn((str(9) + ',' + str(10)), answers)

    def test_sage(self):
        thread_score = Thread.objects.get(id=1).thread_score
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text': 'sdfsdfsf',
                                                                                      'comments_sage': 'on'})

        self.assertEqual(Thread.objects.get(id=1).thread_score, thread_score - 3)

    def test_op(self):
        cookies = self.client.cookies
        cookies['thread1'] = 'op'
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text': 'werwetwetw',
                                                                                      'op': 'on'})

        self.assertEqual('# OP', Comment.objects.get(id=11).comments_op)

    def test_set_active_user_one_thread(self):
        session = self.client.session.session_key
        self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': 1}))
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text': 'qadfsdfsdf'})
        mysession = MySession.objects.get(session_key=session)

        self.assertEqual(mysession.active, 'b')

        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text': 'sdfsdfsdf'})

        self.assertEqual(mysession.active, 'b')

    def test_set_active_user_more_thread(self):
        session = self.client.session.session_key
        self.client.get(reverse('thread', kwargs={'name_board': 'b', 'pk': 1}))
        self.client.post(reverse('AddComment', kwargs={'name_board': 'b', 'pk': 1}), {'comments_text': 'qadfsdfsdf'})
        self.client.post(reverse('AddComment', kwargs={'name_board': 'pr', 'pk': 1}), {'comments_text': 'sdfsdfsdf'})
        mysession = MySession.objects.get(session_key=session)

        self.assertEqual(mysession.active, 'b, pr')


class ViewAjaxTooltip(TestCase):
    fixtures = ['Imageboard.json']

    def test_thread_ajaxtooltip(self):
        response = self.client.get(reverse('AjaxTooltip'), {'type_tooltip': 'thread', 'num_tooltip': 1},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_comment_ajaxtooltip(self):
        response = self.client.get(reverse('AjaxTooltip'), {'type_tooltip': 'comment', 'num_tooltip': 1},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)


class ViewAjaxTooltipComment(TestCase):
    fixtures = ['Imageboard.json']

    def test_smoke(self):
        response = self.client.get(reverse('AjaxTooltipComment'), {'tooltip': 1}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)


class ViewAjaxTooltipThread(TestCase):
    fixtures = ['Imageboard.json']

    def test_smoke(self):
        response = self.client.get(reverse('AjaxTooltipThread'), {'tooltip': 1}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
