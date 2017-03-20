from django.test import TestCase
from ..models import Board, Thread, Comment
from ..forms import CreateThread, AddComment


class ViewIndex(TestCase):

    def test_status_code_index(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class ViewContacts(TestCase):

    def test_status_code_contacts(self):
        response = self.client.get('/contacts.html')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contacts.html')


class ViewThreadList(TestCase):

    def setUp(self):
        board = Board.objects.create(
            board_shortcut='b',
            board_name='Бред',
            board_specification='Бред',
        )
        Thread.objects.create(
            board=board,
            thread_text='sadasda',
        )

    def test_status200_code_ThreadList(self):
        response = self.client.get('/b/')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'board.html')

    def test_status404_code_ThreadList(self):
        response = self.client.get('/zz/')

        self.assertEqual(response.status_code, 404)

    def test_len_thread(self):
        response = self.client.get('/b/')

        self.assertEqual(len(response.context['threads']), 1)

    def test_len_threads(self):
        for x in range(1,6):
            Thread.objects.create(
                board=Board.objects.get(board_shortcut='b'),
                thread_text='sdfsdf',
            )
        response = self.client.get('/b/')

        self.assertEqual(len(response.context['threads']), 5)

    def test_context(self):
        response = self.client.get('/b/')
        form_thread = CreateThread()
        form_comment = AddComment()
        board = Board.objects.get(board_shortcut='b')

        self.assertEqual(str(response.context['form_thread']), str(form_thread))
        self.assertEqual(str(response.context['form_comment']), str(form_comment))
        self.assertEqual(response.context['name_board'], 'b')
        self.assertEqual(response.context['board'], board)

    def test_smoke_ajax(self):
        response = self.client.get('/b/', {'value': '5'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)

    def test_ajax_threads(self):
        for x in range(1, 11):
            Thread.objects.create(
                board=Board.objects.get(board_shortcut='b'),
                thread_text='sdfsdfsdf',
            )
        response = self.client.get('/b/', {'value': '5'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

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
        response = self.client.get('/b/', {'value': '5'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(len(response.json()), 2)

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
        response = self.client.get('/b/', {'value': '5'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(len(response.json()), 4)


class ViewFormAddThread(TestCase):

    def setUp(self):
        Board.objects.create(
            board_name='Bred',
            board_shortcut='b',
            board_specification='Bred',
        )

    def test_smoke(self):
        response = self.client.post('/b/AddThread', {'thread_text': 'thsdnasf'})

        self.assertEqual(response.status_code, 302)

    def test_form(self):
        response = self.client.post('/b/AddThread', {'thread_text': 'thsdnasf'})
        response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)


class ViewAjaxTooltipComment(TestCase):

    def setUp(self):
        board = Board.objects.create(
            board_shortcut='b',
            board_name='Бред',
            board_specification='Бред',
        )
        thread = Thread.objects.create(
            board=board,
            thread_text='sadasda',
        )
        Comment.objects.create(
            thread=thread,
            comments_text='sdfwerwetwt',
        )

    def test_smoke(self):
        response = self.client.get('/AjaxTooltipComment.json', {'tooltip': 1}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)


class ViewAjaxTooltipThread(TestCase):

    def setUp(self):
        board = Board.objects.create(
            board_shortcut='b',
            board_name='Бред',
            board_specification='Бред',
        )
        Thread.objects.create(
            board=board,
            thread_text='sadasda',
        )

    def test_smoke(self):
        response = self.client.get('/AjaxTooltipThread.json', {'tooltip': 1}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)


class ViewAddComment(TestCase):

    def setUp(self):
        board = Board.objects.create(
            board_shortcut='b',
            board_name='Бред',
            board_specification='Бред',
        )
        Thread.objects.create(
            board=board,
            thread_text='sadasda',
        )

    def test_smoke(self):
        response = self.client.post('/b/res/1/AddComment', {'comments_text': 'sdfsdfsdf'})

        self.assertEqual(response.status_code, 302)

    def test_add_comment(self):
        response = self.client.get('/b/res/1.html')
        comments = len(response.context['comments'])
        response = self.client.post('/b/res/1/AddComment', {'comments_text': 'sdfsdfsdf'})
        response = self.client.get('/b/res/1.html')

        self.assertEqual(len(response.context['comments']), comments + 1)

    def test_text_processing_1(self):
        response = self.client.post('/b/res/1/AddComment', {'comments_text': '>>1 (OP) sdfsdf'})
        response = self.client.get('/b/res/1.html')

        self.assertIn('<a class="link-reply" data-num="1 thread">>>1 (OP)</a>', str(response.content))

    def test_text_processing_2(self):
        Comment.objects.create(
            thread=Thread.objects.get(thread_text='sadasda'),
            comments_text='sdfsdtsdf',
        )
        response = self.client.post('/b/res/1/AddComment', {'comments_text': '>>1 sdfsdfsf'})
        response = self.client.get('/b/res/1.html')

        self.assertIn('<a class="link-reply" data-num="1 comment">>>1</a>', str(response.content))

    def test_text_processing_3(self):
        Comment.objects.create(
            thread=Thread.objects.get(thread_text='sadasda'),
            comments_text='sdfsdtsdf',
        )
        response = self.client.post('/b/res/1/AddComment', {'comments_text': '>>1 (OP) sdfsdfsf  >>1'})
        response = self.client.get('/b/res/1.html')

        self.assertIn('<a class="link-reply" data-num="1 thread">>>1 (OP)</a>', str(response.content))
        self.assertIn('<a class="link-reply" data-num="1 comment">>>1</a>', str(response.content))

    def test_answer_for_comments(self):
        Comment.objects.create(
            thread=Thread.objects.get(thread_text='sadasda'),
            comments_text='sdfsdtsdf',
        )
        response = self.client.post('/b/res/1/AddComment', {'comments_text': 'sdfsdfsf  >>1'})
        answers = Comment.objects.get(id=1).comments_answers

        self.assertIn(str(2), answers)

    def test_answer_for_threads(self):
        response = self.client.post('/b/res/1/AddComment', {'comments_text': 'sdfsdfsf  >>1 (OP)'})
        answers = Thread.objects.get(id=1).thread_answers

        self.assertIn(str(1), answers)

    def test_answers_for_comments(self):
        Comment.objects.create(
            thread=Thread.objects.get(thread_text='sadasda'),
            comments_text='sdfsdtsdf',
        )
        response = self.client.post('/b/res/1/AddComment', {'comments_text': 'sdfsdfsf  >>1'})
        response = self.client.post('/b/res/1/AddComment', {'comments_text': 'sdfsewtr  >>1'})
        answers = Comment.objects.get(id=1).comments_answers

        self.assertIn((str(2) + ',' + str(3)), answers)

    def test_answers_for_threads(self):
        response = self.client.post('/b/res/1/AddComment', {'comments_text': 'sdfsdfsf  >>1 (OP)'})
        response = self.client.post('/b/res/1/AddComment', {'comments_text': 'ssdf423s  >>1 (OP)'})
        answers = Thread.objects.get(id=1).thread_answers

        self.assertIn((str(1) + ',' + str(2)), answers)

    def test_sage(self):
        thread_score = Thread.objects.get(id=1).thread_score
        response = self.client.post('/b/res/1/AddComment', {'comments_text': 'sdfsdfsf', 'comments_sage': 'on'})

        self.assertEqual(Thread.objects.get(id=1).thread_score, thread_score - 3)


class ViewAjaxTooltip(TestCase):

    def setUp(self):
        board = Board.objects.create(
            board_shortcut='b',
            board_name='Бред',
            board_specification='Бред',
        )
        thread = Thread.objects.create(
            board=board,
            thread_text='sadasda',
        )
        Comment.objects.create(
            thread=thread,
            comments_text='sdfsdf',
        )

    def test_thread_ajaxtooltip(self):
        response = self.client.get('/AjaxTooltip.json', {'type_tooltip': 'thread', 'num_tooltip': 1},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

    def test_comment_ajaxtooltip(self):
        response = self.client.get('/AjaxTooltip.json', {'type_tooltip': 'comment', 'num_tooltip': 1},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
