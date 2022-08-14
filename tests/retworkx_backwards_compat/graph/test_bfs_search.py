# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import unittest

import retworkx


class TestBfsSearch(unittest.TestCase):
    def setUp(self):
        self.graph = retworkx.PyGraph()
        self.graph.extend_from_edge_list(
            [
                (0, 1),
                (0, 2),
                (1, 3),
                (2, 1),
                (2, 5),
                (2, 6),
                (5, 3),
                (4, 7),
            ]
        )

    def test_graph_bfs_tree_edges(self):
        class TreeEdgesRecorder(retworkx.visit.BFSVisitor):
            def __init__(self):
                self.edges = []

            def tree_edge(self, edge):
                self.edges.append((edge[0], edge[1]))

        vis = TreeEdgesRecorder()
        retworkx.graph_bfs_search(self.graph, [0], vis)
        self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3)])

    def test_graph_bfs_tree_edges_no_starting_point(self):
        class TreeEdgesRecorder(retworkx.visit.BFSVisitor):
            def __init__(self):
                self.edges = []

            def tree_edge(self, edge):
                self.edges.append((edge[0], edge[1]))

        vis = TreeEdgesRecorder()
        retworkx.graph_bfs_search(self.graph, None, vis)
        self.assertEqual(vis.edges, [(0, 2), (0, 1), (2, 6), (2, 5), (1, 3), (4, 7)])

    def test_graph_bfs_tree_edges_restricted(self):
        class TreeEdgesRecorderRestricted(retworkx.visit.BFSVisitor):

            prohibited = [(0, 2), (1, 2)]

            def __init__(self):
                self.edges = []

            def tree_edge(self, edge):
                edge = (edge[0], edge[1])
                if edge in self.prohibited:
                    raise retworkx.visit.PruneSearch
                self.edges.append(edge)

        vis = TreeEdgesRecorderRestricted()
        retworkx.graph_bfs_search(self.graph, [0], vis)
        self.assertEqual(vis.edges, [(0, 1), (1, 3), (3, 5), (5, 2), (2, 6)])

    def test_graph_bfs_goal_search_with_stop_search_exception(self):
        class GoalSearch(retworkx.visit.BFSVisitor):

            goal = 3

            def __init__(self):
                self.parents = {}

            def tree_edge(self, edge):
                u, v, _ = edge
                self.parents[v] = u

                if v == self.goal:
                    raise retworkx.visit.StopSearch

            def reconstruct_path(self):
                v = self.goal
                path = [v]
                while v in self.parents:
                    v = self.parents[v]
                    path.append(v)

                path.reverse()
                return path

        vis = GoalSearch()
        retworkx.graph_bfs_search(self.graph, [0], vis)
        self.assertEqual(vis.reconstruct_path(), [0, 1, 3])

    def test_graph_bfs_goal_search_with_custom_exception(self):
        class StopIfGoalFound(Exception):
            pass

        class GoalSearch(retworkx.visit.BFSVisitor):

            goal = 3

            def __init__(self):
                self.parents = {}

            def tree_edge(self, edge):
                u, v, _ = edge
                self.parents[v] = u

                if v == self.goal:
                    raise StopIfGoalFound

            def reconstruct_path(self):
                v = self.goal
                path = [v]
                while v in self.parents:
                    v = self.parents[v]
                    path.append(v)

                path.reverse()
                return path

        vis = GoalSearch()
        try:
            retworkx.graph_bfs_search(self.graph, [0], vis)
        except StopIfGoalFound:
            pass
        self.assertEqual(vis.reconstruct_path(), [0, 1, 3])

    def test_graph_prune_non_tree_edge(self):
        class PruneNonTreeEdge(retworkx.visit.BFSVisitor):
            def non_tree_edge(self, _):
                raise retworkx.visit.PruneSearch

        vis = PruneNonTreeEdge()
        retworkx.graph_bfs_search(self.graph, [0], vis)

    def test_graph_prune_black_target_edge(self):
        class PruneBlackTargetEdge(retworkx.visit.BFSVisitor):
            def black_target_edge(self, _):
                raise retworkx.visit.PruneSearch

        vis = PruneBlackTargetEdge()
        retworkx.graph_bfs_search(self.graph, [0], vis)

    def test_graph_prune_gray_target_edge(self):
        class PruneGrayTargetEdge(retworkx.visit.BFSVisitor):
            def gray_target_edge(self, _):
                raise retworkx.visit.PruneSearch

        vis = PruneGrayTargetEdge()
        retworkx.graph_bfs_search(self.graph, [0], vis)