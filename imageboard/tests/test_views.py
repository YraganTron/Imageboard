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
        form = CreateThread()
        board = Board.objects.get(board_shortcut='b')

        self.assertEqual(str(response.context['form']), str(form))
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
