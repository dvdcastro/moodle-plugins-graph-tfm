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
 * Version details for the quiz access rule 'oneconnection'.
 *
 * @package     quizaccess_oneconnection
 * @category    upgrade
 * @copyright   2016 Vadim Dvorovenko
 * @copyright   2025 lern.link GmbH <[email]>, Adrian Sarmas, Vadym Nersesov
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'quizaccess_oneconnection';
$plugin->version = 2026030200; // Plugin version (date-based).
$plugin->release = '5.1.1';
$plugin->maturity = MATURITY_STABLE;
$plugin->requires = 2025041400; // Moodle 5.0.
