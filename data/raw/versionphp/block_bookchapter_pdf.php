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
 * Version information for block_bookchapter_pdf
 *
 * @package    block_bookchapter_pdf
 * @copyright  2024 Luca <[email]>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();
$plugin->component = 'block_bookchapter_pdf';
$plugin->version = 2024102500;
$plugin->requires = 2020061500; // Requires this Moodle version (3.9 or higher).
$plugin->maturity = MATURITY_STABLE;
$plugin->release = 'v4.4';
$plugin->dependencies = array(
    'mod_book' => 2020061500
);
