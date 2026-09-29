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
 * Plugin for Moodle tinymce html_components.
 *
 * @package    tiny_html_components
 * @author  2023 Anthony Durif, Gerbault Cédric
 * @copyright 2023 Anthony Durif,Gerbault Cédric Université Clermont Auvergne
 * @license   http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();
$plugin->version = 2025030201; // The current plugin version (Date: YYYYMMDDXX).
$plugin->requires = 2022112801; // 2017111300 is Moodle 3.4.0.
$plugin->component = 'tiny_html_components';
$plugin->maturity = MATURITY_STABLE;
$plugin->release = 'v4.5';
