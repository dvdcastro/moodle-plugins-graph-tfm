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
 * Random select answers question type version file.
 *
 * @package   qtype_answersselect
 * @copyright 2022-2025 Joseph Rézeau <[email]>
 * @license   http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();


$plugin->version   = 2025041901;
$plugin->requires  = 2021051700;
$plugin->component = 'qtype_answersselect';
$plugin->maturity  = MATURITY_STABLE;
$plugin->release   = '5.0';
$plugin->dependencies = [
    'qtype_multichoice' => 2020061500,
];
