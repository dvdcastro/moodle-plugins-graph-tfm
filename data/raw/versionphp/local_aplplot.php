<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * Version details.
 *
 * @package     local_aplplot
 * @author      Valery Fremaux <[email]>
 * @copyright   2026 onwards Valery Fremaux (https://www.activeprolearn.com)
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version  = 2026060801;   // The (date) version of this plugin.
$plugin->requires = 2022112801;   // Requires this Moodle version.
$plugin->component = 'local_aplplot';
$plugin->release = '5.1.0 (Build 2026060801)';   // Release.
$plugin->maturity = MATURITY_RC;
$plugin->supported = [500, 503];

// Non moodle attributes.
<<<<<<< HEAD
$plugin->codeincrement = '4.5.0002';
$plugin->privacy = 'public';
=======
$plugin->codeincrement = '5.1.0002';
$plugin->privacy = 'private';
>>>>>>> MOODLE_501_STABLE
