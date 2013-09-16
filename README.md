Sublime Mozc Input
==================

This is Sublime Text 2/3 Plugin for Using Mozc(`mozc_server`) 
via `mozc_emacs_helper`

Though this plugin is intended to be used on Linux,
it may work on the other platforms.

Requirements
------------

* [Mozc](https://code.google.com/p/mozc/)
* emacs-mozc


Screenshot
----------

![Movie](http://yasuyuky.github.io/SublimeMozcInput/images/mozc_movie.gif)





Installation
------------

1. Install Mozc and emacs-mozc (see official instruction)
2. Check out the project and Copy `Mozc Input` directory 
   to your **Packages** directory



### Package Control
Currently not unavalable

### Install plugin from github
This is exsample.

	cd /path/to/your/repo/directory
    git clone git://guthub.com/yasuyuky/SublimeMozcInput
	cd /path/to/your/packages/directory
	ln -s /path/to/your/repo/directory/SublimeMozcInput/Input Mozc

### Install Mozc to Linux Using Package Control
#### Debian/Ubuntu

    sudo apt-get install mozc emacs-mozc

#### Fedora/Enterprize Linux(including CentOS)
choose and add repository (.repo) file 
from http://download.opensuse.org/repositories/home:/sawaa/
to your /etc/yum.repos.d/

    sudo yum install mozc emacs-mozc



Usage
-----

### Basic Usage

* `ctrl+¥` to toggle `mozc_mode`
* Press any character key to enter `mozc_input_mode `
* `mozc_input_mode`
  * `space` key to convert
  * `tab` key to show suggest


### Set keybind to toggle mozc mode

Default keybind to `toggle_mozc` on OSX/Linux is `ctrl+¥`

To change this, set your keybind file 
(`Preferences` -> `Key Bindings - User`) like this.

    { "keys": ["ctrl+space"], "command": "toggle_mozc" }



### Optional Keybindings

Kotoeri like keybindings sample

    // Convert to Hiragana
    {"keys": ["ctrl+j"],
     "command": "mozc_send_key",
     "args": {"key": "f6"},
     "context": [{"key": "mozc_input_mode"}]},
     
    // Convert to Katakana
    {"keys": ["ctrl+k"],
     "command": "mozc_send_key",
     "args": {"key": "f7"},
     "context": [{"key": "mozc_input_mode"}]},
     
	// Convert to Zenkaku
    {"keys": ["ctrl+l"],
     "command": "mozc_send_key",
     "args": {"key": "f9"},
     "context": [{"key": "mozc_input_mode"}]},

	// Convert to Hankaku
    {"keys":["ctrl+;"],
     "command": "mozc_send_key",
     "args": {"key": "f10"},
     "context": [{"key": "mozc_input_mode"}]},

	// Activate/Deactivate mozc_mode
    {"keys": ["ctrl+/"], "command": "activate_mozc"},
    {"keys": ["ctrl+:"], "command": "deactivate_mozc"}

### Optional Settings

Set optional settings in **MozcInput.sublime-settings**.
You can access via `Preferences` -> `Package Settings` 
-> `Mozc Input` -> `Settings - User`


    {
      "mozc_emacs_helper": "/path/to/mozc_emacs_helper",
      // default: "mozc_emacs_helper"
      // or you can use mozc_emacs_helper over ssh
      // "mozc_emacs_helper": "ssh hostname mozc_emacs_helper",

      "mozc_mode_line": "[日本語]",
      // default: "[Mozc]"

      "mozc_input_mode_line": "[入力中]",
      // default: "✎Mozc"

      "mozc_highlight_style": "function",
      // default: "comment"

      "mozc_use_quick_panel": false
      // default: true
      // if you don't wanna use quick_panel for suggest
    }


Feedback
--------

This plugin is tested on Ubuntu12.04 and Mac OSX.

If you find a problem on your environment, report it.


@yasuyuky on Twitter


