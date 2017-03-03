from django.db import models


class Board(models.Model):
    class Meta:
        ordering = ['board_shortcut', ]

    board_shortcut = models.CharField(max_length=10)
    board_name = models.TextField()
    board_specification = models.TextField()
    board_posts = models.IntegerField(default=0)
    board_in_hour = models.IntegerField(default=0)
    board_active_24hour = models.IntegerField(default=0)

    def __str__(self):
        return self.board_shortcut


class Thread(models.Model):
    class Meta:
        ordering = ['-thread_time', ]

    board = models.ForeignKey(Board)
    thread_tittle = models.CharField(max_length=255, blank=True)
    thread_text = models.TextField()
    thread_image = models.ImageField(blank=True)
    thread_time = models.DateTimeField(auto_now_add=True)
    thread_score = models.IntegerField(default=0)
    thread_answers = models.TextField(blank=True)

    def __str__(self):
        if self.thread_tittle == '':
            return str(self.id)
        else:
            return self.thread_tittle


class Comment(models.Model):

    thread = models.ForeignKey(Thread)
    comments_tittle = models.CharField(max_length=100, blank=True)
    comments_text = models.TextField()
    comments_image = models.ImageField(blank=True)
    comments_time = models.DateTimeField(auto_now_add=True)
    comments_op = models.CharField(max_length=5, blank=True)
    comments_answers = models.TextField(blank=True)
