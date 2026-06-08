import datetime
import re

JOURNAL_TYPES = ['科普', '人文', '财经', '时尚', '体育', '其他']
JOURNAL_FREQUENCIES = ['月刊', '季刊', '年刊', '周刊']
ISSUE_STATUS_AVAILABLE = '在库'
ISSUE_STATUS_BORROWED = '借出'

PHONE_MASK_PATTERN = re.compile(r'^\d{4}xxxx\d{4}$|^\d{3}xxxx\d{4}$')


def validate_journal_type(journal_type):
    if journal_type not in JOURNAL_TYPES:
        raise ValueError(
            f'期刊类型必须是以下之一: {", ".join(JOURNAL_TYPES)}'
        )
    return journal_type


def validate_frequency(frequency):
    if frequency not in JOURNAL_FREQUENCIES:
        raise ValueError(
            f'发刊频率必须是以下之一: {", ".join(JOURNAL_FREQUENCIES)}'
        )
    return frequency


def validate_date(date_str):
    try:
        return parse_date(date_str)
    except ValueError:
        raise ValueError(f'日期格式错误，应为 YYYY-MM-DD: {date_str}')


def validate_phone(phone):
    if not phone:
        raise ValueError('手机号不能为空')
    if 'xxxx' not in phone and 'XXXX' not in phone:
        if len(phone) != 11 or not phone.isdigit():
            raise ValueError(f'手机号格式错误: {phone}')
    return phone


def validate_days(days):
    try:
        d = int(days)
        if d <= 0:
            raise ValueError
        return d
    except (ValueError, TypeError):
        raise ValueError(f'借阅天数必须是正整数: {days}')


def create_journal(name, journal_type, publisher, frequency):
    return {
        'name': name,
        'type': validate_journal_type(journal_type),
        'publisher': publisher,
        'frequency': validate_frequency(frequency),
        'issues': []
    }


def create_issue(issue_name, receive_date):
    return {
        'issue': issue_name,
        'receive_date': str(validate_date(receive_date)),
        'status': ISSUE_STATUS_AVAILABLE,
        'borrower': None,
        'phone': None,
        'borrow_date': None,
        'due_date': None,
        'return_date': None
    }


def parse_date(date_str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()


def calculate_overdue_days(issue):
    if issue['status'] != ISSUE_STATUS_BORROWED:
        return 0
    if not issue['due_date']:
        return 0
    today = datetime.date.today()
    due_date = parse_date(issue['due_date'])
    delta = (today - due_date).days
    return max(0, delta)


def check_issue_exists(journal, issue_name):
    for issue in journal['issues']:
        if issue['issue'] == issue_name:
            return issue
    return None


def add_journal(journals, name, journal_type, publisher, frequency):
    for j in journals:
        if j['name'] == name:
            raise ValueError(f'期刊已存在: {name}')
    validate_journal_type(journal_type)
    validate_frequency(frequency)
    journal = create_journal(name, journal_type, publisher, frequency)
    journals.append(journal)
    return journal


def receive_issue(journals, journal_name, issue_name, receive_date):
    journal = None
    for j in journals:
        if j['name'] == journal_name:
            journal = j
            break
    if not journal:
        raise ValueError(f'期刊不存在: {journal_name}')
    if check_issue_exists(journal, issue_name):
        raise ValueError(f'该期已登记: {journal_name} {issue_name}')
    issue = create_issue(issue_name, receive_date)
    journal['issues'].append(issue)
    return issue


def borrow_issue(journals, journal_name, issue_name, borrower, phone, days):
    journal = None
    for j in journals:
        if j['name'] == journal_name:
            journal = j
            break
    if not journal:
        raise ValueError(f'期刊不存在: {journal_name}')
    issue = check_issue_exists(journal, issue_name)
    if not issue:
        raise ValueError(f'该期未登记: {journal_name} {issue_name}')
    if issue['status'] == ISSUE_STATUS_BORROWED:
        raise ValueError(f'该期刊已被借出，无法重复借阅')
    if issue['status'] != ISSUE_STATUS_AVAILABLE:
        raise ValueError(f'该期刊当前状态为 {issue["status"]}，不可借阅')
    days = validate_days(days)
    phone = validate_phone(phone)
    today = datetime.date.today()
    due_date = today + datetime.timedelta(days=days)
    issue['status'] = ISSUE_STATUS_BORROWED
    issue['borrower'] = borrower
    issue['phone'] = phone
    issue['borrow_date'] = str(today)
    issue['due_date'] = str(due_date)
    issue['return_date'] = None
    return issue


def return_issue(journals, journal_name, issue_name):
    journal = None
    for j in journals:
        if j['name'] == journal_name:
            journal = j
            break
    if not journal:
        raise ValueError(f'期刊不存在: {journal_name}')
    issue = check_issue_exists(journal, issue_name)
    if not issue:
        raise ValueError(f'该期未登记: {journal_name} {issue_name}')
    if issue['status'] != ISSUE_STATUS_BORROWED:
        raise ValueError(f'该期刊当前未借出，状态: {issue["status"]}')
    today = datetime.date.today()
    issue['status'] = ISSUE_STATUS_AVAILABLE
    issue['return_date'] = str(today)
    return issue


def get_overdue_issues(journals):
    overdue_list = []
    for journal in journals:
        for issue in journal['issues']:
            overdue_days = calculate_overdue_days(issue)
            if overdue_days > 0:
                overdue_list.append({
                    'journal_name': journal['name'],
                    'issue': issue['issue'],
                    'borrower': issue['borrower'],
                    'phone': issue['phone'],
                    'due_date': issue['due_date'],
                    'overdue_days': overdue_days
                })
    return overdue_list


def get_stats(journals):
    type_stats = {t: 0 for t in JOURNAL_TYPES}
    freq_stats = {f: 0 for f in JOURNAL_FREQUENCIES}
    for journal in journals:
        type_stats[journal['type']] += 1
        freq_stats[journal['frequency']] += 1
    return {
        'total': len(journals),
        'by_type': type_stats,
        'by_frequency': freq_stats
    }
