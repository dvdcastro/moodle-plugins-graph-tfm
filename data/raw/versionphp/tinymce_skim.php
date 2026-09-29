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
 * TinyMCE Skim Import version details.
 *
 * @package   tinymce_skim
 * @copyright 2013 Justin Hunt
 * @license   http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

// The current plugin version (Date: YYYYMMDDXX).
$plugin->version   = 2018041000;
// Required Moodle version.
$plugin->requires  = 2012112900;
// Component Name - Moodle uses this as unique id for plugin
$plugin->component = 'tinymce_skim';
//beta
$plugin->maturity  = MATURITY_BETA;
// Human readable version informatiomn
$plugin->release   = '1.1.0(Build 2018041000)';