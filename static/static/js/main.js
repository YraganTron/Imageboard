/**
 * Created by pc on 24.11.16.
 */

$(document).ready(function() {

    function make_list(data, x) {
        if (data[x].model == 'boards.comment') {
            if (data[x].fields.comments_answers == '') return '';
            if (data[x].fields.comments_answers.indexOf(',')) {
                return data[x].fields.comments_answers.split(',');
            } else {
                var arr = [];
                arr.push(data[x].fields.comments_answers);
                return arr;
            }
        } else {
            if (data[x].fields.thread_answers == '') return '';
            if (data[x].fields.thread_answers.indexOf(',')) {
                return data[x].fields.thread_answers.split(',');
            } else {
                var arr = [];
                arr.push(data[x].fields.thread_answers);
                return arr;
            }
        }
    }

    var display_var_1 = 0;
    var display_var_2 = 0;
    $('#js_thr_1').click(function () {
        if (display_var_1 == 0) {
            $('.container-js_1').css("display", "block");
            $(this).text('Закрыть форму постинга');
            $().add('<hr id="containerform">').appendTo('div.container-form_1');
            display_var_1 = 1;
        } else if (display_var_1 == 1) {
            $('.container-js_1').css("display", "none");
            $(this).text('Cоздать тред');
            $('div.container-form_1 hr#containerform').remove();
            display_var_1 = 0;
            }
        });
    $('#js_thr_2').click(function () {
        if (display_var_2 == 0) {
            $('.container-js_2').css("display", "block");
            $(this).text('Закрыть форму постинга');
            $().add('<hr id="containerform">').appendTo('div.container-form_2');
            display_var_2 = 1;
        } else if (display_var_2 == 1) {
            $('.container-js_2').css("display", "none");
            $(this).text('Создать тред');
            $('div.container-form_2 hr#containerform').remove();
            display_var_2 = 0;
        }
    });

    $('.reply').click(function() {
        var comment = $(this).attr('data-num');
        $.ajax({
            type: 'GET',
            dataType: 'json',
            data: {'tooltip': comment},
            url: '/AjaxTooltipComment.json',
            success: function (data) {
                var url = data[0].fields.thread + '.html';
                $('.container-js_3').attr("action", "res/" + url);
            }
        });

        var text = $('.form_control').val() + '>>' + comment + '\n';
        $('.form_control').val(text);
        $('.form-fixed').css({
            "display": "block"
        });
    });

    $('.thread_answer').click(function () {
        var thread = $(this).attr('data-num');
        if (!$('.container-js_3').attr("action")) {
            $.ajax({
                type: 'GET',
                dataType: 'json',
                data: {'tooltip': thread},
                url: '/AjaxTooltipThread.json',
                success: function (data) {
                    var url = 'res/' + data[0].pk + '.html';
                    $('.container-js_3').attr('action', url);
                }
            });
        }

        var text = $('.form_control').val() + '>>' + $(this).attr('data-num') + ' (OP)' + '\n';
        $('.form_control').val(text);
        $('.form-fixed').css({
            "display": "block"
        });

    });

    $('#form-fixed-close').click(function () {
        $('.form-fixed').css("display", "none");
    });

    $('.form-fixed').draggable({
        containment: "window",
        handle: ".form-fixed-header",
    });

    function parse_datetime(data, y) {
        if (data[y].model == 'boards.comment') {
            var parser_T = data[y].fields.comments_time.split('T');
            var parser_date = parser_T[0].split('-');
            var month = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
            var parser_time = parser_T[1].split(':');
            var datetime = parser_date[2] + ' ' + month[parser_date[1] - 1] + ' ' + parser_date[0] + ' г. ' + parser_time[0] + ':' + parser_time[1];
            data[y].fields.comments_time = datetime;
            return data;
        }
        if (data[y].model == 'boards.thread') {
            var parser_T = data[y].fields.thread_time.split('T');
            var parser_date = parser_T[0].split('-');
            var month = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
            var parser_time = parser_T[1].split(':');
            var datetime = parser_date[2] + ' ' +  month[parser_date[1] - 1] + ' ' + parser_date[0] + ' г. ' + parser_time[0] + ':' + parser_time[1];
            data[y].fields.thread_time = datetime;
            return data;
        }
    }

    var count_comment = 5;
    if ($('.container_board_index').length >= 5) {
        $(window).scroll(function () {
            if($(window).scrollTop() + $(window).height() == $(document).height()) {
                $.ajax({
                    type: 'GET',
                    dataType: 'json',
                    data: {'value': count_comment},
                    success: function (data) {
                        for (var i = 0; i <= 4; i++) {
                            if (data[i].model == 'boards.thread') {
                                parse_datetime(data, i);
                                var tmpl = _.template(document.getElementById('template-thread').innerHTML);
                                var result = tmpl({data: data, i: i});
                                $('.dynamic1').append(result);
                                for (var y = 0; y <= (data.length - 1); y++) {
                                    status_hr = 0;
                                    if (data[y].model == 'boards.comment') {
                                        if(data[y].fields.thread == data[i].pk) {
                                            parse_datetime(data, y);
                                            var answers = make_list(data, y);
                                            var tmpl_2 = _.template(document.getElementById('template-comment').innerHTML);
                                            var rsl = tmpl_2({data: data, y: y, answers: answers});
                                            $('.dynamic1').append(rsl);
                                            status_hr = 1;
                                        }
                                        if (y == data.length - 1 && status_hr == 1) {
                                            $('.dynamic1').append('<hr class="comments">');
                                            status_hr = 0;
                                        }
                                    }
                                }
                            }
                        }
                        count_comment += 5;
                    }
                })
            }
        })
    }

    $('.dynamic1').on('mouseover', 'a.link-reply', function () {
        var tooltip = $(this).data('num');
        tooltip = String(tooltip).split(' ');
        var num_tooltip = tooltip[0];
        var type_tooltip = tooltip[1];
        var some_link_reply = $(this);
        $.ajax({
            type: 'GET',
            dataType: 'json',
            data: {
                'num_tooltip': num_tooltip,
                'type_tooltip': type_tooltip,
            },
            url: '/AjaxTooltip.json',
            success: function (data) {
                parse_datetime(data, 0);
                var answers = make_list(data, 0);
                var left = some_link_reply.offset().left + 10;
                var top = some_link_reply.offset().top + 10;
                if (type_tooltip == 'thread') {
                    var tmpl = _.template(document.getElementById('template-tooltip-thread').innerHTML);
                    var result = tmpl({data: data, answers: answers, left_thread: left, top_thread: top});
                    var idthread = 'tooltip_thread' + data[0].pk;
                    var test = document.getElementById(idthread);
                    if (test == null) {
                        $('.dynamic1').append(result);
                    } else {
                        $(test).remove();
                        $('.dynamic1').append(result);
                    }
                } else {
                    var tmpl = _.template(document.getElementById('template-tooltip-comment').innerHTML);
                    var result = tmpl({data: data, answers: answers, left_comment: left, top_comment: top});
                    var idcomment = 'tooltip_comment' + data[0].pk;
                    var test = document.getElementById(idcomment);
                    if (test == null) {
                        $('.dynamic1').append(result);
                    } else {
                        $(test).remove();
                        $('.dynamic1').append(result);
                    }
                }
            }
        });
    });

    $('.dynamic1').on('click', function() {
        $('.tooltip').remove();
    });

});