from django.test import TestCase

from ..models import Board, Comment, Thread


class ModelBoard(TestCase):

    def setUp(self):
        Board.objects.create(
            board_shortcut='pr',
            board_name='Программирование',
            board_specification='Смерть си',
        )

    def test_str_method_board(self):
        board = Board.objects.get(board_shortcut='pr')

        self.assertEqual(str(board), board.board_shortcut)


class ModelThread(TestCase):

    def setUp(self):
        board = Board.objects.create(
            board_shortcut='pr',
            board_name='Программирование',
            board_specification='Смерть си',
        )
        Thread.objects.create(
            board=board,
            thread_text='cool test',
        )
        Thread.objects.create(
            board=board,
            thread_tittle='cool tittle',
            thread_text='cool test 2',
        )

    def test_str_method_thread(self):
        thread_1 = Thread.objects.get(thread_text='cool test')
        thread_2 = Thread.objects.get(thread_text='cool test 2')

        self.assertEqual(str(thread_1), str(thread_1.id))
        self.assertEqual(str(thread_2), thread_2.thread_tittle)

    def test_save_method_thread(self):
        board = Board.objects.get(board_shortcut='pr')
        thread = Thread.objects.get(thread_text='cool test')
        thread.thread_tittle = 'WEBM'
        thread.save()

        self.assertEqual(board.board_posts, 2)


class ModelComment(TestCase):

    def setUp(self):
        board = Board.objects.create(
            board_shortcut='pr',
            board_name='Программирование',
            board_specification='Смерть си',
        )
        thread = Thread.objects.create(
            board=board,
            thread_text='cool test',
        )
        Comment.objects.create(
            thread=thread,
            comments_text='One',
        )

    def test_save_method_comment(self):
        board = Board.objects.get(board_shortcut='pr')
        comment = Comment.objects.get(comments_text='One')
        comment.comments_text = 'Two'
        comment.save()

        self.assertEqual(board.board_posts, 2)
