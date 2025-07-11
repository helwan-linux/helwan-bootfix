# Maintainer: Saeed Badrelden <saeedbadrelden2021@gmail.com>
pkgname=helwan-bootfix
pkgver=1.0.0
pkgrel=1
pkgdesc="Simple Boot Repair Utility for Helwan Linux"
arch=('any')
url="https://github.com/helwan-linux/helwan-bootfix"
license=('GPL3')
depends=('python' 'python-pyqt5')
makedepends=('git')
source=("$pkgname::git+$url.git")
md5sums=('SKIP')

package() {
  cd "$srcdir/$pkgname/hel-bootfix"

  # تثبيت السكريبت التنفيذي
  install -Dm755 helbootfix.py "$pkgdir/usr/bin/hel-bootfix"

  # تثبيت ملفات البرنامج
  install -d "$pkgdir/usr/share/helwan-bootfix"
  cp -r assets logic tabs diagram.txt "$pkgdir/usr/share/helwan-bootfix"

  # تثبيت ملف .desktop
  install -Dm644 hel-bootfix.desktop "$pkgdir/usr/share/applications/hel-bootfix.desktop"

  # تثبيت الأيقونة في pixmaps (بدون الحاجة لتحديث الكاش)
  install -Dm644 assets/icon.png "$pkgdir/usr/share/pixmaps/hel-bootfix.png"
}

