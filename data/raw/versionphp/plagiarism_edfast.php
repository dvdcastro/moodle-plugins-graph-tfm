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
 * EdFast Moodle 4.0+ Plagiarism Plugin - Version & Metadata
 *
 * @package    plagiarism_edfast
 * @copyright  2026 EdFast
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'plagiarism_edfast';
$plugin->version = 2026032800;                   // 2026-03-28.00 — Fix all moodle.org code review issues
$plugin->release = '1.4.15 (Moodle 4.0-5.1)';
$plugin->requires = 2022041900;                  // Moodle 4.0 minimum (released 2022-04-19)
$plugin->requires_php = '8.0';                  // PHP 8.0 minimum for Moodle 4.0+
$plugin->maturity = MATURITY_STABLE;             // Stable release
$plugin->cron = 300;                            // Run cron every 5 minutes
$plugin->supported = [400, 501];                // Moodle 4.0-5.1

$plugin->author = 'EdFast';
$plugin->copyright = '2026 EdFast';
$plugin->license = 'GPL-3.0-or-later';
$plugin->url = 'https://edfast.ai';
