<?php
// This file is part of Moodle - https://moodle.org/
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
// along with Moodle.  If not, see <https://www.gnu.org/licenses/>.

/**
 * Plugin version and other meta-data are defined here.
 *
 * @package     block_ask4summary
 * @author      Mohammed Saleh
 * @copyright   2022 Athabasca University
 * @license     https://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'block_ask4summary';
$plugin->version = 2022061300;
// Moodle 3.3.3 for mtrace statements. This may lower later if removed.
$plugin->requires = 2017051503;
// Added Privacy API requirements.
$plugin->release = 'v0.1.3';
$plugin->maturity = MATURITY_STABLE;
