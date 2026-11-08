# Native runtime audit — Telescope Desk

Retained third-party native files match the baseline bytes. Unknown dynamic/fallback usage is retained.
A = core, D = optional implemented feature, F = unresolved. Microsoft rights remain OPEN.

| File | Version | Class | Role/evidence | SHA256 |
|---|---|---|---|---|
| _internal/_asyncio.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | c77de90cad749087a0c5dc5e19d78d24f6ef44e7e5ac19b8420cfc0cea62395d |
| _internal/_bz2.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 65f610646d10d5babea080e060d244b546ec52c54012e5e937dc72dcc2e2e7bc |
| _internal/_cffi_backend.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 9af5e4f68a41f26b726f2e9424f9d58a4f5666189f6a48be95f406b257102aec |
| _internal/_ctypes.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 0e56107a891100535f2da79d85a5ae65ff1227b4765bd108f8593ac1a1110d81 |
| _internal/_decimal.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | aeacfead2befcc0768063a037bb64bd32109ae09cb144e5f571b04dd7965db9d |
| _internal/_elementtree.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 5009a9a53c03ef8387443b5cf6ce08e5c3a79727466a0b931c5bbca915bf89ca |
| _internal/_hashlib.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 03d233dbace599168eaffec823de6ed7beec8c2a4ebfe9b8a3d8e042a59af3ba |
| _internal/_lzma.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | e3deecc1f59a3b811c608861decd84de1e8df8bafd5e2b39188861318c5a38cf |
| _internal/_multiprocessing.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 2c636df7059cb0dd7e978dd735c7c5c8ddb09cf94754cf9e232296b96c5c545a |
| _internal/_overlapped.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 662126ff80c3a1b4cedf74074029c12ae4743e6d3b37376e39ac70aacb7d4d3c |
| _internal/_queue.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 48e76e0ad63f6932b4a77b5819f41c1e7595636ca8d9e824f0943a14b8bb5035 |
| _internal/_socket.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 3efa4636cf9e350856f6927d67a4c2564bf9bd2758a00bbf17d3aece5b60016d |
| _internal/_sqlite3.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 64b51df2805c58b023a875e8ae3be7ac7f61ef664f32ca6c90f6315da47ef0bc |
| _internal/_ssl.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 0bc527d2dbc50009f43b2ed5d5982c4f63f4b647647ffa9eda612dcda80f6040 |
| _internal/_uuid.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | acce4f281d7ffb2dec0997527faf25b1df62ad7bd3032c568ddcf65c90edc867 |
| _internal/_wmi.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | a980f1e7a29842bd946863fc2693fbeb555a9dc0f9e1630dfed9a2fcdef3ece2 |
| _internal/_zoneinfo.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 76f1439cda82ab6976df6ba505c4079444703f6d44d8b0259ce59c0ff4279fb4 |
| _internal/astropy/compiler_version.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | f568d2a0ddcf16219c4ed1f077d3b4466b4223830364d9b4002863710e892bef |
| _internal/astropy/convolution/_convolve.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 3be23d81518de0763d2c4d86fedb5700af64879bdf5f7fd022f58634dd96da9c |
| _internal/astropy/cosmology/_src/flrw/scalar_inv_efuncs.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 81a358e652b593486e5c3f43def6b4863a16f9c2d877dfe50a59713e0c81b3c9 |
| _internal/astropy/cosmology/_src/signature_deprecations.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | dc0e67ae8738c53011695de438a89b65a7eec1a7426738a194210ba4452e2992 |
| _internal/astropy/io/ascii/cparser.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | fa9fefda0fb7a1f2922e5f2d6b79be7f85ac2faaa9ca1e811a99f213f1f90038 |
| _internal/astropy/io/fits/_utils.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | bc9290be91b1e47cd54184db362d4e50764a6ee833cfbe99b0f45e2e5e879a0f |
| _internal/astropy/io/fits/hdu/compressed/_compression.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 5cfb7635e3fde774b7575c0b6548735381c59ad5bec9c983b13abcc3b34a0a2d |
| _internal/astropy/io/votable/fast_converters.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 5207236b8bc2e2c9d51600bf83c47c849cfcf883bf9894f8f9439b0afa7ef285 |
| _internal/astropy/io/votable/tablewriter.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | ac74436862659a4500dca8a6bd540799c9f25887ca43fc2fd63aa02e82eb5144 |
| _internal/astropy/stats/_fast_sigma_clip.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | f1b2bc875b89921607950edd1e70231030a1569d8098692dbaffb9de68e41f99 |
| _internal/astropy/stats/_stats.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 78fc8dba571e34713336b9d9878ba15d2fc3033f3850cf31e491f21a4bacd247 |
| _internal/astropy/table/_column_mixins.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | f16f2ffbbd847f4101715866ce0edaf955ced5f0dcc95274d9a6d488c6c0dc95 |
| _internal/astropy/table/_np_utils.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 874574c1b658c82f9a53f5f6354b675275447f0fca341e89e1b6191a17e357ee |
| _internal/astropy/time/_parse_times.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | cd6f0a3febdfc0b1d3dc63573c53a0128af5c58c0a7441cd62ed46b9a4360665 |
| _internal/astropy/timeseries/periodograms/bls/_impl.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | f4dd84b2b9caea2c31c9711b29683c1ebb214416de20fff503c9c79f5a62eee9 |
| _internal/astropy/timeseries/periodograms/lombscargle/implementations/cython_impl.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | a61a671bec1fa6e98e32000bef0bf85f984005bd90970e4d1659fa7f73fcd253 |
| _internal/astropy/utils/xml/_iterparser.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 60dfcd87ddee393d6fc5df61c6598973080e399d01061217b4887e0a9e5c6163 |
| _internal/astropy/wcs/_wcs.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 24e725e63b516663ead40dd4e1e1093c009f6f2a4229a9254b38e75af93a8472 |
| _internal/charset_normalizer/cd.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 2bdbc0805f85565d76f8d6166e451bfafa6d5490b06b36c9f423cd0102b4f149 |
| _internal/charset_normalizer/md.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | b08be5d29125f39a92e22d0abe4b9160753f7a790fffd07258319a8e16394afa |
| _internal/cryptography/hazmat/bindings/_rust.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 1d4332a447cab13dec8e3a533ad579e0e562b79e40822c931f33769758fc7156 |
| _internal/erfa/ufunc.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | e048837cf3fd1517135d176d44b1cddffe95caac033f4db25802247386c3ba05 |
| _internal/libcrypto-3.dll | 3.0.16 | F | Retained: ownership/import evidence in selected release audit | ccfffddcd3defb8d899026298af9af43bc186130f8483d77e97c93233d5f27d7 |
| _internal/libffi-8.dll | not declared | F | Retained: ownership/import evidence in selected release audit | eff52743773eb550fcc6ce3efc37c85724502233b6b002a35496d828bd7b280a |
| _internal/libssl-3.dll | 3.0.16 | F | Retained: ownership/import evidence in selected release audit | 007142039f04d04e0ed607bda53de095e5bc6a8a10d26ecedde94ea7d2d7eefe |
| _internal/numpy/_core/_multiarray_tests.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | f09f60242eaed510e1af6384284f53ff56ae42770a62e630bd415bc2b6854d66 |
| _internal/numpy/_core/_multiarray_umath.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 9c10617e66e992b5ac6d9f78fe7cedd0011618e1c2f89d09a185bb63073e2c90 |
| _internal/numpy/fft/_pocketfft_umath.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 4f008612d6b9e2ab3820ee17a1c758c499e45e80a36764c9dfb7bf304b066f03 |
| _internal/numpy/linalg/_umath_linalg.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 03bc9de2d6d8e2d9ea3ec781f3c16bcbc9960095cc02ca588f4229cd1560c661 |
| _internal/numpy/random/_bounded_integers.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 927c1673ba698a85e6253b4d8d2223eb019b021792c54604489767c694d2ab93 |
| _internal/numpy/random/_common.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 712a7bb4b2d3e56548cdf255eb4e6c1ca0737d7d81d76f09bdccebb0703ae572 |
| _internal/numpy/random/_generator.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 0fa509dcf5ae21910cb2b3c74271977d0fac7fab15ffd5f32017e08b97e71de6 |
| _internal/numpy/random/_mt19937.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | e6938df4dd3a193b7d9171d3e192702be3a70de2ebe866cf6fcd92f9e368349d |
| _internal/numpy/random/_pcg64.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 8eb5569b221d40884093def83d897376bddd99c9279f182b9db3145b9b897d34 |
| _internal/numpy/random/_philox.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | cc0c03e2c1443e8981300ddb9cc5ceb504e7f8494323d4ec0a1ad95ae16fbf75 |
| _internal/numpy/random/_sfc64.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 20c551734cd2b2be2425c8773b795f1e92de8826ebbe6c1103cd0fa6b5c94408 |
| _internal/numpy/random/bit_generator.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | c7f637df1fa0db9fe4bba6c05dac680d89aed245401423f1ffd16d93366a35a7 |
| _internal/numpy/random/mtrand.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | e8bdaf22830ceaabc596854a816d39d96d1d60e96c2e12a9a17950b624d480a1 |
| _internal/numpy.libs/libscipy_openblas64_-ed4f167a5330424524f45258e7ca2c8d.dll | not declared | F | Retained: ownership/import evidence in selected release audit | ed4f167a5330424524f45258e7ca2c8d7f03c0cba1f30ee4985553ac1f88ecf8 |
| _internal/numpy.libs/msvcp140-a4c2229bdc2a2a630acdc095b4d86008.dll | 14.40.33810.0 | A | Compiler ABI runtime; different paths/versions preserved | a4c2229bdc2a2a630acdc095b4d86008e5c3e3bc7773174354f3da4f5beb9cde |
| _internal/PIL/_imaging.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 7140f56d38dd6cd51512f8122386bcb914c5df2a82eb5f719c973527d9213cee |
| _internal/PIL/_imagingcms.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 2640857cace64d69735bdcaa3987e9ad70f85168abc1a8662079c77ac44b5301 |
| _internal/PIL/_imagingtk.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | e1c87f73e96d2269395624d03b3808300f4b0f795f5fad1ecc3d1492e5dcc7c2 |
| _internal/PIL/_webp.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | bb9c64d38a6e4857bd3358e14dbe6cf3a4593b1efcd1185fdba1ef8931550896 |
| _internal/pyexpat.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | d615e193d1affcdbfe504e90d3621cbdcff94bf72b79d899126534507fd6d27a |
| _internal/PySide6/avcodec-63.dll | 63.1.101 | D | Live View Qt/FFmpeg, RTSP and ABI dependency | fd6b08a07310d34a6be4349172557f5a234bd66420e28934b625b669a763ba2f |
| _internal/PySide6/avformat-63.dll | 63.1.101 | D | Live View Qt/FFmpeg, RTSP and ABI dependency | 8a38846c7420f94aa85b4d87dae7d97d5c54a5cdb9eb6c5eb1c7b40a86e2ab8b |
| _internal/PySide6/avutil-61.dll | 61.1.101 | D | Live View Qt/FFmpeg, RTSP and ABI dependency | 2538cdbed7a6d2c8d1219bf1a79412e6bf657d16ce5759b62df3182813f4e4dc |
| _internal/PySide6/MSVCP140.dll | 14.44.35211.0 | A | Compiler ABI runtime; different paths/versions preserved | f6f1d55bfd64027820ddce48f9cd8cf46d53bfa34047e6acf4ef348d492a05cb |
| _internal/PySide6/MSVCP140_1.dll | 14.44.35211.0 | A | Compiler ABI runtime; different paths/versions preserved | 2be87527c41e1ba8aff48e326e0adcd4743516e0bbcc9304986c726e27de6aca |
| _internal/PySide6/MSVCP140_2.dll | 14.44.35211.0 | A | Compiler ABI runtime; different paths/versions preserved | 6a72ed8a87eae1671640bd1ca98eccb989f1772ae46ab84594e385bf6d4ac4fb |
| _internal/PySide6/opengl32sw.dll | not declared | D | Software rendering fallback; no clean software-only host tested | 18aedc7a4b610f53bcc7b7a5c5ed9293c7e86f030e3273ad54ed3bb1ebd36702 |
| _internal/PySide6/plugins/generic/qtuiotouchplugin.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 8565656807db29cfb6170e6803181f24e0bed3aa1b14684d29694e375cc5ee96 |
| _internal/PySide6/plugins/iconengines/qsvgicon.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | f9e21af351bd5d5629bc00e8e3796b552eca92d1a9645438c865b9c53af1714f |
| _internal/PySide6/plugins/imageformats/qgif.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 77782de4aa4f7b75a7cc4d3f24aee49da935c312ea13d25f4cda3a98d180145c |
| _internal/PySide6/plugins/imageformats/qicns.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 93e2e588cd1036af3c6300b539d648b3825625788e59a3f0f1863d9901c9759f |
| _internal/PySide6/plugins/imageformats/qico.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | a0e4d0d0319e075f6cc5f774084bf390f7af83600f38685c6bc9c407681cc22c |
| _internal/PySide6/plugins/imageformats/qjpeg.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | dd42bdcd229744a9515db82ba9a802c74b6589cc508c3e85fb30f06ba24b9da6 |
| _internal/PySide6/plugins/imageformats/qsvg.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | b63f97ed0ae60aa5bc332c37e429c1f31154e1eee358352b2c49598c5269843b |
| _internal/PySide6/plugins/imageformats/qtga.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | ce95aa019d940533341b4f08a10ddd3b0393162678c47904251da77aeadfd34e |
| _internal/PySide6/plugins/imageformats/qtiff.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | ce696a2dd2e57b8852f7d01834725f54a4d0be66c3d2c491df60fd907fece907 |
| _internal/PySide6/plugins/imageformats/qwbmp.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | e118243bd3528aa5fe6378a8839abe0efc200e891af06ee369b97b2ff239b89c |
| _internal/PySide6/plugins/imageformats/qwebp.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 02ae5555b688f78aade5cedcd66c646b73d519460c008c23e75ad408bd152668 |
| _internal/PySide6/plugins/multimedia/ffmpegmediaplugin.dll | 6.12.0.0 | D | Live View Qt/FFmpeg, RTSP and ABI dependency | a29ceb3a6ce93b85e02e19133eb5f34d9588d29eb46d3e80458bd7c693bc492e |
| _internal/PySide6/plugins/multimedia/windowsmediaplugin.dll | 6.12.0.0 | D | Live View Qt/FFmpeg, RTSP and ABI dependency | 74c91f3b38ce3fe31e0bce53f6032cb54607431f878eeb18e1c8463e41785f2f |
| _internal/PySide6/plugins/networkinformation/qnetworklistmanager.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 2bd047476183c76004221fb44adb7ada9b4b6ce5c2929d63ff67a5305b430f1a |
| _internal/PySide6/plugins/platforms/qdirect2d.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 18213464be5a5a1d39af6a2c876ce21a6bb6a634c814651d09f0ef7e4719edc2 |
| _internal/PySide6/plugins/platforms/qminimal.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | c9025bc5f4653c5aadac87f06ab391763e82adf792f6759c6027a78a5efcaf5c |
| _internal/PySide6/plugins/platforms/qoffscreen.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | d24ef380ab0882d39f21539dcf57ab4213875a6fc658a53012f2d2fd275c6f69 |
| _internal/PySide6/plugins/platforms/qwindows.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | ddd5cf6a96f058cfafcbc901ddeb5df010d755f0716beacfb557f8b27b733afe |
| _internal/PySide6/plugins/styles/qmodernwindowsstyle.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 74d4c47b56a942afb3723bb105900501bb8f91a46a8b592fa722cc4fdb2ce9bf |
| _internal/PySide6/plugins/tls/qcertonlybackend.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 87574d467b6f9640a15e37bf4183179c6a7cefc4dc84346b8f4cffb989cf1e12 |
| _internal/PySide6/plugins/tls/qopensslbackend.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 94b3492bc4087da2818e2749a5a03f7d810611b2e3648bd8d580ad087363046f |
| _internal/PySide6/plugins/tls/qschannelbackend.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 2915a86a2531e65fd4905f0cc1c8dc353772a4f52aeda5100725dd9249db54d1 |
| _internal/PySide6/pyside6.abi3.dll | not declared | F | Retained: ownership/import evidence in selected release audit | d5b87ccb0a7c305854bd120242b0a75002d0b50a35532d0f6171e4ed0f3cc82a |
| _internal/PySide6/Qt6Core.dll | 6.12.0.0 | A | Core GUI/Python runtime | f57ed38afd95d0306cca9d88d997f639f70c7628a4f1f064eae291d579487121 |
| _internal/PySide6/Qt6Gui.dll | 6.12.0.0 | A | Core GUI/Python runtime | abd20026e190e8cc69667d1bea042db05cd353cc05e7da74b063c20b7da3f6cd |
| _internal/PySide6/Qt6Multimedia.dll | 6.12.0.0 | D | Live View Qt/FFmpeg, RTSP and ABI dependency | 7629a499b204fcc71a96e12c7180b0a8a920d05ee2f2b20bbec1a819610a69b0 |
| _internal/PySide6/Qt6Network.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 1c7c393b264ae78f4dee211656377a086c4be714bf768d3135f94f11c1d0be61 |
| _internal/PySide6/Qt6OpenGL.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 788b743bfaca141ca83e28c161646d51de92a71adf7a86c653c36fdea5a9bf5b |
| _internal/PySide6/Qt6Svg.dll | 6.12.0.0 | F | Retained: ownership/import evidence in selected release audit | 8f1de5b28aab1eedb415c751c81f9cfaa2804242868c0ceea5f3fdb4b2babca4 |
| _internal/PySide6/Qt6Widgets.dll | 6.12.0.0 | A | Core GUI/Python runtime | 2f62cbe2869fff4e20df7369c2786e1ec7ec290d5a63d1371b7f70cf06909c3f |
| _internal/PySide6/QtCore.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 6486f6f0a2fec42fc8c652c0b76bb3ad0d44eaccad9c72e577116a075681eebb |
| _internal/PySide6/QtGui.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 9ac544d1bcf8a26c408c63090d05506f8382d5378ee3a204e29a3ac5449c5b2b |
| _internal/PySide6/QtMultimedia.pyd | not declared | D | Live View Qt/FFmpeg, RTSP and ABI dependency | 5bfe26ab9df1d13c70d8421f6a81816b44f0587b1980f8eca7451bfc27f98c8c |
| _internal/PySide6/QtNetwork.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 22bffdb2a431b5a986de255f7eb0fcd1fd7d9e85c53967978e2ab479b33a13c5 |
| _internal/PySide6/QtWidgets.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | a8e323e56a93c1a8a70981c36a409c0a2546e7a08da5be8ca4e03dfd27febc2a |
| _internal/PySide6/swresample-7.dll | 7.1.101 | D | Live View Qt/FFmpeg, RTSP and ABI dependency | a7c667837f334c9d2820ec95c89e7cdf0205698e45341537b3ae6c761d9be1dc |
| _internal/PySide6/swscale-10.dll | 10.1.101 | D | Live View Qt/FFmpeg, RTSP and ABI dependency | a6142d95cb96f8397fcc6b99142a674a5f0417206de40091b43a64024b734658 |
| _internal/PySide6/VCRUNTIME140.dll | 14.44.35211.0 | A | Compiler ABI runtime; different paths/versions preserved | a36e0cb185eb89533ed96d4568138f86a1315756a8b2644c5963a8ce23e32101 |
| _internal/PySide6/VCRUNTIME140_1.dll | 14.44.35211.0 | A | Compiler ABI runtime; different paths/versions preserved | 302b1e160e858602490a55e32ae2e29ddfc0bec2a188e19550cb655cdaa58f9c |
| _internal/python3.dll | 3.12.10 | A | Core GUI/Python runtime | fb975a606e7fbf74f64260e3f60c3490b4f74a183c0926fd6ed1ac4c52ac7b1c |
| _internal/python312.dll | 3.12.10 | A | Core GUI/Python runtime | 9a0e3435aaa680d868150f87ab3e388ad2eebc22f87e036155c7b4eda8cd2120 |
| _internal/select.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | d4d7181b11db0bd22a6cd5cda6f8583d1f5c77615fd0a6ca33350619d6e0438a |
| _internal/shiboken6/MSVCP140.dll | 14.44.35211.0 | A | Compiler ABI runtime; different paths/versions preserved | 1ba4d7c0a95d375da138a057a57593b33510ad5bda6c5e2686afd68faa5b4231 |
| _internal/shiboken6/Shiboken.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 8ccf415b2cefb5b6462504581ab1993fb41afe04e415931d8a72049f1c79b267 |
| _internal/shiboken6/shiboken6.abi3.dll | not declared | F | Retained: ownership/import evidence in selected release audit | 07c318c02be5a3a9f1475f5a2d0cd438f4d4ea3288c28e2e10bc5ebbbec8de86 |
| _internal/shiboken6/VCRUNTIME140.dll | 14.44.35211.0 | A | Compiler ABI runtime; different paths/versions preserved | e7be9112ee9a5b9f44b44bff24cb761cca9b1ed7550b612f77b70edfcf5fdabf |
| _internal/shiboken6/VCRUNTIME140_1.dll | 14.44.35211.0 | A | Compiler ABI runtime; different paths/versions preserved | f02cd4a862b85a9a3153d27e15e5a213f5df8e3d77004ed2e87b8a7e8873d97c |
| _internal/sqlite3.dll | 3.49.1.0 | F | Retained: ownership/import evidence in selected release audit | 8daa45684bf6688fca28d956b2e8942f2fa98f656675ce68e6d61dd869848a7a |
| _internal/unicodedata.pyd | 3.12.10 | F | Retained: ownership/import evidence in selected release audit | 208ee1cd3cbad0828433ca7246b05be2b1ff5569983d27d296c0b38888585488 |
| _internal/VCRUNTIME140.dll | 14.42.34438.0 | A | Compiler ABI runtime; different paths/versions preserved | 052ad6a20d375957e82aa6a3c441ea548d89be0981516ca7eb306e063d5027f4 |
| _internal/VCRUNTIME140_1.dll | 14.42.34438.0 | A | Compiler ABI runtime; different paths/versions preserved | 6a99bc0128e0c7d6cbbf615fcc26909565e17d4ca3451b97f8987f9c6acbc6c8 |
| _internal/winrt/_winrt.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 96dce74f66e213ac5fbeaa6476d2b757e7e4df33d1e9827f78f60f9623f5fdfe |
| _internal/winrt/_winrt_windows_devices_geolocation.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | ed63b6832f4adc26ed0fdde8d6a7a4d74f6683c9893d8933964a6459c573ac8f |
| _internal/winrt/_winrt_windows_foundation.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 3c7ac22bbe09103f8dfbf728f01f2a00ddb462eb3a28052fa9c54e4721ff7b9d |
| _internal/winrt/_winrt_windows_foundation_collections.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | c3ab35abf3d7b9807cf29ecc018667b01026621da587bb9a476f8c309adda01f |
| _internal/winrt/MSVCP140.dll | 14.29.30157.0 built by: cloudtest | A | Compiler ABI runtime; different paths/versions preserved | 75872c426555ac8af55b5a7f6d4aea8831af74353b22612850a2bfc40e3b67e1 |
| _internal/yaml/_yaml.cp312-win_amd64.pyd | not declared | F | Retained: ownership/import evidence in selected release audit | 4fd0e84f50261ed0886cffcdd8008b055af3352546e649c3d741b50eae1f9b5f |
| TelescopeDesk.exe | 2.3.0b3 | F | Retained: ownership/import evidence in selected release audit | 2eac7e4994230a37165631628323e8560dbc2041d2b74bd663e6ca07f8ac3a1f |
