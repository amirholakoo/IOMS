#!/usr/bin/env python
"""
🧪 اجراکننده تست‌های HomayOMS
📋 اجرای کامل تست‌ها با pytest و unittest برای دستیابی به 90% coverage
🎯 گزارش‌گیری جامع و تحلیل پوشش کد
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# تنظیم مسیر Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HomayOMS.settings.local')

import django
django.setup()

def run_command(cmd, description):
    """اجرای دستور و نمایش نتیجه"""
    print(f"\n🔄 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ خطا در اجرای دستور: {e}")
        return False

def run_pytest_tests(markers=None, verbose=True):
    """اجرای تست‌های pytest"""
    cmd = "python -m pytest"
    
    if verbose:
        cmd += " -v"
    
    if markers:
        cmd += f" -m '{markers}'"
    
    cmd += " --tb=short --cov=. --cov-report=term-missing"
    
    return run_command(cmd, f"اجرای تست‌های pytest{' با مارکر ' + markers if markers else ''}")

def run_unittest_tests():
    """اجرای تست‌های unittest"""
    cmd = "python manage.py test --verbosity=2"
    return run_command(cmd, "اجرای تست‌های Django unittest")

def run_coverage_report():
    """تولید گزارش پوشش کد"""
    cmd = "coverage report --show-missing"
    return run_command(cmd, "گزارش پوشش کد")

def run_coverage_html():
    """تولید گزارش HTML پوشش کد"""
    cmd = "coverage html"
    result = run_command(cmd, "تولید گزارش HTML پوشش کد")
    if result:
        print("📊 گزارش HTML در htmlcov/index.html ایجاد شد")
    return result

def main():
    """تابع اصلی"""
    parser = argparse.ArgumentParser(description='اجراکننده تست‌های HomayOMS')
    parser.add_argument('--pytest-only', action='store_true', help='فقط pytest اجرا شود')
    parser.add_argument('--unittest-only', action='store_true', help='فقط unittest اجرا شود')
    parser.add_argument('--markers', type=str, help='مارکرهای pytest (مثال: unit,integration)')
    parser.add_argument('--no-coverage', action='store_true', help='بدون گزارش پوشش کد')
    parser.add_argument('--html-report', action='store_true', help='تولید گزارش HTML')
    
    args = parser.parse_args()
    
    print("🧪 شروع اجرای تست‌های HomayOMS")
    print("🎯 هدف: دستیابی به 90% پوشش کد")
    print("=" * 60)
    
    success = True
    
    if args.unittest_only:
        success &= run_unittest_tests()
    elif args.pytest_only:
        success &= run_pytest_tests(args.markers)
    else:
        # اجرای هر دو
        print("\n📋 مرحله 1: اجرای تست‌های unittest")
        success &= run_unittest_tests()
        
        print("\n📋 مرحله 2: اجرای تست‌های pytest")
        success &= run_pytest_tests(args.markers)
    
    if not args.no_coverage:
        print("\n📊 مرحله 3: تولید گزارش پوشش کد")
        success &= run_coverage_report()
        
        if args.html_report:
            success &= run_coverage_html()
    
    # اجرای تست‌های مارکر-بندی شده
    if not args.markers:
        print("\n🎭 مرحله 4: اجرای تست‌های دسته‌بندی شده")
        
        test_categories = [
            ('unit', 'تست‌های واحد'),
            ('integration', 'تست‌های یکپارچگی'),
            ('permissions', 'تست‌های مجوزها'),
            ('payments', 'تست‌های پرداخت'),
            ('user_creation', 'تست‌های ایجاد کاربر'),
        ]
        
        for marker, description in test_categories:
            print(f"\n🔍 اجرای {description}")
            run_pytest_tests(marker, verbose=False)
    
    # خلاصه نهایی
    print("\n" + "=" * 60)
    if success:
        print("✅ همه تست‌ها با موفقیت اجرا شدند!")
        print("🎯 برای مشاهده گزارش کامل: coverage report")
        if args.html_report:
            print("🌐 برای مشاهده گزارش HTML: firefox htmlcov/index.html")
    else:
        print("❌ برخی تست‌ها ناموفق بودند!")
        print("🔍 لطفاً خروجی بالا را بررسی کنید")
    
    print("=" * 60)
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 