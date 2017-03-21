from imageboard.models import MySession, Board


def count_usr(sender, **kwargs):
    boards = Board.objects.all()
    for x in boards:
        x.board_in_hour = MySession.objects.filter(name_board__contains=x.board_shortcut).count()
        x.save()


def active(sender, **kwargs):
    boards = Board.objects.all()
    for x in boards:
        x.board_active_24hour = MySession.objects.filter(active__contains=x.board_shortcut).count()
        x.save()
