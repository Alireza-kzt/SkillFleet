# راهنمای فارسی SkillFleet

SkillFleet فهرست مهارت‌ها، نسخه‌های بررسی‌شده و ابزار مدیریت مشترک را نگه می‌دارد.
انتخاب مهارت‌ها و دستورهای اختصاصی هر پروژه داخل همان پروژه ذخیره می‌شود.
هستهٔ پیش‌فرض فقط دو مهارت دارد؛ بسته‌های دیگر را متناسب با کار اضافه کنید.

## نصب یک‌باره

Python نسخهٔ ۳٫۱۰ به بالا و Git لازم است. مخزن را بیرون پروژه‌ها کلون کنید:

```bash
git clone https://github.com/Alireza-kzt/SkillFleet.git
```

مثلاً در ویندوز مخزن را در `C:/Tools/SkillFleet` نگه دارید. داخل پروژهٔ مقصد اجرا کنید:

```powershell
py -3 C:/Tools/SkillFleet/skillfleet.py init --profile python --profile research --profile notebook
py -3 C:/Tools/SkillFleet/skillfleet.py doctor
```

در لینوکس و macOS از `python3 /path/to/SkillFleet/skillfleet.py` استفاده کنید.
برای انتخاب چند بسته، `--profile` را تکرار کنید. اگر حذفش کنید، نوع پروژه از فایل‌های
شناخته‌شده تشخیص داده می‌شود؛ پژوهشی یا سازمانی بودن پروژه باید صریح انتخاب شود.

## نمونهٔ ترکیب‌ها

| نوع پروژه | آرگومان اتصال |
| --- | --- |
| پژوهش و آموزش مدل | `--profile python --profile research --profile notebook` |
| مقاله و پایان‌نامه | `--profile academic --profile documents` |
| تولید پلان و آزمایش‌های ML | `--profile python --profile research --profile ml` |
| محصول وب فارسی | `--profile web --profile design --profile rtl` |
| Flutter و GetX | `--profile flutter --profile rtl` |
| خدمات Cloudflare | `--profile web --profile cloudflare --profile security` |
| مدیریت تیم و اسپرینت | `--profile organization` |
| تولید ویدیو و دمو | `--profile video` |

برای Claude Code، `--agent claude-code` اضافه کنید؛ برای اتصال همزمان،
`--agent codex --agent claude-code` بدهید. Codex پیش‌فرض است و Cursor مسیر مشترک دارد.
بسته‌های انتخابی، محیط Flutter، GPU، PyTorch، رندرکنندهٔ فایل یا کلید API نصب نمی‌کنند.
پیش‌نیازهای هر مهارت در فهرست ثبت شده است.

## پس از اتصال

فایل‌های `skillfleet.json` و `skillfleet.lock.json`، پوشهٔ مهارت‌های نصب‌شده،
دستورالعمل کوتاه و تغییر `AGENTS.md` را در گیت خود پروژه کامیت کنید.
فایل‌های قبلی پروژه حفظ می‌شوند؛ اگر فایل تحت مدیریت را تغییر داده باشید، ابزار
برای حفظ تغییرات شما عملیات جایگزینی را متوقف می‌کند.

دستورهای زیر بعد از نصب اختیاری با `pip install -e` کوتاه نوشته شده‌اند؛ می‌توانید
به‌جای `skillfleet` همان دستور کامل Python و مسیر فایل را استفاده کنید:

```bash
skillfleet list
skillfleet add systematic-debugging
skillfleet remove systematic-debugging
skillfleet sync
skillfleet doctor
```

`sync` نسخه‌های ثابت همان پروژه را نگه می‌دارد. به‌روزرسانی مخزن مرکزی به‌تنهایی
انتخاب یا نسخهٔ مهارت‌های پروژه‌های دیگر را تغییر نمی‌دهد.

## به‌روزرسانی با بررسی تغییرات

```bash
git -C /path/to/SkillFleet pull --ff-only
skillfleet check
skillfleet update
```

فایل `.skillfleet/update.diff` را بررسی کنید، سپس:

```bash
skillfleet update --apply
skillfleet doctor
```

بعد از آزمون‌های مرتبط، تغییرات را در پروژه کامیت کنید. برای بازگشت آخرین عملیات:

```bash
skillfleet rollback
```

مخزن مرکزی گردش‌کار هفتگی بررسی منابع و ساخت Draft PR دارد. ادغام آن و ارتقای
پروژه‌ها خودکار نیست؛ برای ساخت PR باید دسترسی مربوط به GitHub Actions فعال باشد.

## کیفیت و مصرف توکن

دستورهای مهارت‌ها روی نام‌گذاری طبیعی، سادگی، مرز ماژول‌ها، حذف پیچیدگی اضافی،
بازتولید آزمایش و بررسی واقعی نتیجه تأکید می‌کنند. با انتخاب محدود مهارت‌ها و
خواندن مرجع‌ها هنگام نیاز، بار متن اضافی کمتر می‌شود. این‌ها دستورالعمل رفتاری‌اند؛
تضمین کیفیت کد، پذیرش مقاله یا درصد مشخص صرفه‌جویی توکن نیستند.

برای تغییر اختصاصی هر پروژه، دستور را در `AGENTS.md` همان پروژه بنویسید؛
نیازی به اضافه‌کردن تنظیمات آن پروژه به SkillFleet نیست.
