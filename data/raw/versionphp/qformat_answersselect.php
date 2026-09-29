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
 * Plugin for changing multichoice to answersselect when importing Moodle XML.
 *
 * @package    qformat_answersselect
 * @copyright  2021 Joseph Rézeau <[email]>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'qformat_answersselect';
$plugin->version   = 2025042000;
$plugin->requires  = 2016120500;
$plugin->release   = '5.0';
$plugin->maturity = MATURITY_STABLE;

$plugin->dependencies = [
    'qformat_xml' => 2016120500,
    'qtype_answersselect' => 2021082200,
];
