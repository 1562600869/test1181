import argparse
import sys

from models import (
    JOURNAL_TYPES,
    JOURNAL_FREQUENCIES,
    add_journal,
    receive_issue,
    borrow_issue,
    return_issue,
    get_overdue_issues,
    get_stats
)
from storage import load_journals, save_journals


def cmd_add_journal(args):
    journals = load_journals()
    journal = add_journal(
        journals,
        args.name,
        args.type,
        args.publisher,
        args.frequency
    )
    save_journals(journals)
    print(f'已添加期刊: {journal["name"]}')
    print(f'  类型: {journal["type"]}')
    print(f'  出版社: {journal["publisher"]}')
    print(f'  频率: {journal["frequency"]}')


def cmd_receive(args):
    journals = load_journals()
    issue = receive_issue(
        journals,
        args.journal_name,
        args.issue,
        args.date
    )
    save_journals(journals)
    print(f'已登记到刊: {args.journal_name} {issue["issue"]}')
    print(f'  到刊日期: {issue["receive_date"]}')
    print(f'  状态: {issue["status"]}')


def cmd_borrow(args):
    journals = load_journals()
    issue = borrow_issue(
        journals,
        args.journal_name,
        args.issue,
        args.borrower,
        args.phone,
        args.days
    )
    save_journals(journals)
    print(f'已完成借阅: {args.journal_name} {issue["issue"]}')
    print(f'  借阅人: {issue["borrower"]}')
    print(f'  联系电话: {issue["phone"]}')
    print(f'  借阅日期: {issue["borrow_date"]}')
    print(f'  应还日期: {issue["due_date"]}')
    print(f'  状态: {issue["status"]}')


def cmd_return(args):
    journals = load_journals()
    issue = return_issue(
        journals,
        args.journal_name,
        args.issue
    )
    save_journals(journals)
    print(f'已完成归还: {args.journal_name} {issue["issue"]}')
    print(f'  归还日期: {issue["return_date"]}')
    print(f'  状态: {issue["status"]}')


def cmd_overdue(args):
    journals = load_journals()
    overdue_list = get_overdue_issues(journals)
    if not overdue_list:
        print('暂无超期未还的期刊')
        return
    print(f'共有 {len(overdue_list)} 本超期未还的期刊:')
    print('-' * 60)
    for item in overdue_list:
        print(f'期刊: {item["journal_name"]} {item["issue"]}')
        print(f'  借阅人: {item["borrower"]}')
        print(f'  联系电话: {item["phone"]}')
        print(f'  应还日期: {item["due_date"]}')
        print(f'  超期天数: {item["overdue_days"]} 天')
        print('-' * 60)


def cmd_stats(args):
    journals = load_journals()
    stats = get_stats(journals)
    print(f'期刊总数: {stats["total"]}')
    print()
    print('按类型分布:')
    for jtype, count in stats['by_type'].items():
        print(f'  {jtype}: {count}')
    print()
    print('按发刊频率分布:')
    for freq, count in stats['by_frequency'].items():
        print(f'  {freq}: {count}')


def build_parser():
    parser = argparse.ArgumentParser(
        description='社区图书馆期刊订阅和借阅管理工具'
    )
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    subparsers.required = True

    add_parser = subparsers.add_parser('add-journal', help='添加新期刊')
    add_parser.add_argument('name', help='期刊名称')
    add_parser.add_argument(
        '--type',
        required=True,
        choices=JOURNAL_TYPES,
        help=f'期刊类型: {", ".join(JOURNAL_TYPES)}'
    )
    add_parser.add_argument('--publisher', required=True, help='出版社')
    add_parser.add_argument(
        '--frequency',
        required=True,
        choices=JOURNAL_FREQUENCIES,
        help=f'发刊频率: {", ".join(JOURNAL_FREQUENCIES)}'
    )
    add_parser.set_defaults(func=cmd_add_journal)

    receive_parser = subparsers.add_parser('receive', help='登记到刊')
    receive_parser.add_argument('journal_name', help='期刊名称')
    receive_parser.add_argument('--issue', required=True, help='刊期，如 2024年3月号')
    receive_parser.add_argument('--date', required=True, help='到刊日期，格式 YYYY-MM-DD')
    receive_parser.set_defaults(func=cmd_receive)

    borrow_parser = subparsers.add_parser('borrow', help='借阅期刊')
    borrow_parser.add_argument('journal_name', help='期刊名称')
    borrow_parser.add_argument('--issue', required=True, help='刊期，如 2024年3月号')
    borrow_parser.add_argument('--borrower', required=True, help='借阅人姓名')
    borrow_parser.add_argument('--phone', required=True, help='联系电话')
    borrow_parser.add_argument('--days', required=True, help='借阅天数')
    borrow_parser.set_defaults(func=cmd_borrow)

    return_parser = subparsers.add_parser('return', help='归还期刊')
    return_parser.add_argument('journal_name', help='期刊名称')
    return_parser.add_argument('--issue', required=True, help='刊期，如 2024年3月号')
    return_parser.set_defaults(func=cmd_return)

    overdue_parser = subparsers.add_parser('overdue', help='查看超期未还期刊')
    overdue_parser.set_defaults(func=cmd_overdue)

    stats_parser = subparsers.add_parser('stats', help='查看统计信息')
    stats_parser.set_defaults(func=cmd_stats)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except ValueError as e:
        print(f'错误: {e}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'未知错误: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
