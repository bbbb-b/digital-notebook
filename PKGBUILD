# Maintainer: bbbb-b <nullptr@inbox.lt>

pkgname='digital-notebook-git'
pkgver=r16.fd89548
pkgrel=1
pkgdesc="A Digital Notebook for storing and querying everyday information"
arch=(x86_64) 
url="https:/github.com/bbbb-b/digital-notebook"
license=('GPL3') 
depends=('python' 'python-pip' 'python-recordclass' 'python-humanize' 'python-pytimeparse' 'python-pyperclip')
makedepends=('git')
provides=()
conflicts=()
replaces=()
backup=()
options=()
source=("$pkgname::git+https://github.com/bbbb-b/digital-notebook")
noextract=()
md5sums=("SKIP")

pkgver() {
	cd "$pkgname"
	printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)" 
	# change to last commit date? 
}

package() {
	cd "$pkgname"
	#ls
	#cp -r "./digital_notebook/" "$pkgdir/opt/$pkgname"
	mkdir -p "$pkgdir/opt/$pkgname/"
	find digital_notebook -type f -exec install -Dm 644 "{}" "$pkgdir/opt/$pkgname/" \;
	chmod 755 "$pkgdir/opt/$pkgname/__main__.py"
	mkdir -p "$pkgdir/usr/bin/"
	ln -s "/opt/$pkgname/__main__.py" "$pkgdir/usr/bin/digital-notebook"
}
