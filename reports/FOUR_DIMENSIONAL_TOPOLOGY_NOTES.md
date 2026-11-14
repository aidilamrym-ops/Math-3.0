# Catatan Topologi 4-Dimensi dan Batas Klaim Math 3.0

Dokumen ini menyertai sertifikat `lean/spec_v4/EvenUnimodularObstruction.lean`
(Fase 52). Tujuannya adalah memisahkan dengan tegas:

1. fakta matematika yang benar-benar diformalkan dan diperiksa kernel Lean 4;
2. bayangan aljabar dari teorema Donaldson;
3. klaim populer yang **tidak** dibuktikan oleh repositori ini.

## 1. Konteks: Donaldson, bentuk irisan, dan dimensi empat

Pada awal 1980-an, Simon Donaldson (lahir 1957) membuktikan teorema
diagonalisasi untuk bentuk irisan manifold 4-dimensi halus tertentu.
Teorema itu menghubungkan topologi halus dengan ruang moduli koneksi
Yang--Mills anti-self-dual. Bersama karya Freedman tentang manifold
topologis 4-dimensi, hasil ini menunjukkan bahwa kategori topologis dan
kategori halus tidak berperilaku sama di dimensi empat.

Yang belum selesai sampai sekarang adalah **smooth 4-dimensional Poincare
conjecture (SPC4)**: apakah setiap 4-manifold halus tertutup yang
homeomorfik ke $S^4$ sebenarnya diffeomorfik ke $S^4$? Eksistensi struktur
halus eksotis pada $S^4$ masih terbuka. Sebaliknya, eksistensi struktur
halus eksotis pada $\mathbb{R}^4$ sudah terbukti (Gompf, Taubes), dan
fakta bahwa $\mathbb{R}^n$ hanya memiliki struktur halus unik untuk
$n \ne 4$ adalah hasil klasik.

## 2. Yang diformalkan di Lean

Sertifikat `EvenUnimodularObstruction.lean` membuktikan obstruksi paritas
murni untuk bentuk kuadratik integral:

- definisi bentuk genap: $Q_G(x) = x^T G x$ selalu genap;
- jika $D$ diagonal dan genap, maka setiap entri diagonalnya genap,
  sehingga $2^n \mid \det D$;
- jika $D = P^T G P$ dengan $P$ unimodular atas $\mathbb{Z}$ dan
  $\det G = \pm 1$, maka $\det D = \pm 1$;
- untuk $n > 0$, $2^n$ tidak membagi $\pm 1$, sehingga kontradiksi.

Akibatnya, bentuk genap unimodular tidak dapat didiagonalisasi oleh
kongruensi unimodular atas $\mathbb{Z}$ pada rank positif.

Witness konkretnya adalah

$$H = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix},$$

intersection form dari $S^2 \times S^2$. Bentuk ini genap,
$\det H = -1$, tetapi bukan bentuk diagonal atas $\mathbb{Z}$.

## 3. Yang tidak diklaim

Repositori ini **tidak** membuktikan:

- teorema diagonalisasi Donaldson;
- teorema Freedman atau klasifikasi manifold topologis 4-dimensi;
- SPC4, baik versi topologis maupun halus;
- eksistensi atau ketiadaan struktur halus eksotis pada $S^4$;
- hubungan penuh antara ruang moduli instanton dan bentuk irisan.

Sertifikat Lean di atas adalah **bayangan aljabar** dari obstruksi paritas.
Ia tidak memuat analisis PDE, teori indeks, ruang moduli, atau konstruksi
manifold halus. Karena itu, hasil ini tidak boleh dikutip sebagai bukti
teorema Donaldson atau sebagai penyelesaian masalah Millennium apa pun.

## 4. Catatan tentang E8

Bentuk E8 adalah bentuk genap unimodular definit positif berank 8 dengan
determinan 1. Secara aljabar, E8 juga tidak dapat didiagonalisasi atas
$\mathbb{Z}$ dengan argumen paritas yang sama. Namun, sertifikat Fase 52
belum memuat E8 karena perhitungan determinan matriks Cartan $8 \times 8$
belum disertifikasi secara efisien di kernel tanpa memakai jalur komputasi
yang tidak diizinkan oleh kebijakan trust-token repositori. Witness $H$
sudah cukup untuk menunjukkan obstruksi non-diagonalisasi secara rigor.

## 5. Rujukan konseptual

- S. K. Donaldson, *An application of gauge theory to four-dimensional
  topology*, Journal of Differential Geometry 18 (1983).
- M. H. Freedman, *The topology of four-dimensional manifolds*, Journal of
  Differential Geometry 17 (1982).
- R. E. Gompf, *Three exotic $R^4$'s and other anomalies*, Journal of
  Differential Geometry 18 (1983).
- C. H. Taubes, *Gauge theory on asymptotically periodic 4-manifolds*,
  Journal of Differential Geometry 25 (1987).

Rujukan ini adalah konteks matematis, bukan klaim bahwa repositori telah
memformalkan isinya.
