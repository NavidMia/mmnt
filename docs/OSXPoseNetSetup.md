### Setting up tf open pose on MacOSX

* Clone from *github.com//ildoonet/tf-pose-estimation*
* Make virtualenv with *-p python3* flag
* Source activate from *~/virtualenv/< myvenvname >/bin* OR *workon < myvenvname >*
* Pip install all that good stuff at the top of the repo README.md
* Iterm2 - v3.2.5 **required**
* OSX Security will not let your camera device be known to ITerm https://gitlab.com/gnachman/iterm2/issues/7194
	* From OSX Terminal while iterm closed: 'tccutil reset Camera && tccutil reset Microphone'
	* Launch iterm,	run Imagesnap to get camera permissions
* Brew install wget
	* Get the graph files in models/graph/cmu, then run 'bash download.sh'
* Test with 'python run_webcam.py --model=mobilenet_thin --resize=432x368 --camera=0'
	* 2018 MBP Touch Bar should have enough power for a 2fps demo