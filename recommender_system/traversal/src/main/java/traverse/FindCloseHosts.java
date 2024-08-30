package traverse;

import org.neo4j.graphdb.*;
import org.neo4j.graphdb.traversal.*;
import org.neo4j.procedure.*;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;


public class FindCloseHosts {

    // node labels
    static final Label IP = Label.label("IP");
    static final Label OrganizationUnit = Label.label("OrganizationUnit");
    static final Label Contact = Label.label("Contact");

    // relationship types
    static final RelationshipType HAS = RelationshipType.withName("HAS");
    static final RelationshipType PART_OF = RelationshipType.withName("PART_OF");

    @Context
    public Transaction tx;

    /**
     * Traverse from attacked host's IP and finds IP of close hosts, to maximum depth given as a parameter.
     *
     * @param initIp       Attacked host's IP
     * @param maxDepth Maximum depth to traverse
     * @return Stream of FindCloseHostsRecord containing ip node, path types and distance
     */
    @Procedure(value = "traverse.findCloseHosts", mode = Mode.READ)
    @Description("traverse starting from the node with the given IP address and returns all close IPs")
    public Stream<CloseHostRecord> findCloseHosts(@Name("ipAddress") String initIp,
                                                       @Name("maxDepth") Long maxDepth) {

        // Find attacked host IP node
        Node attackedHost = tx.findNodes(IP, "address", initIp)
                .stream()
                .findFirst()
                .orElseThrow(IllegalArgumentException::new);

        // BFS from given host
        Traverser traverse = tx.traversalDescription()
                .breadthFirst()
                .uniqueness(Uniqueness.NONE)
                .relationships(HAS, Direction.BOTH)
                .relationships(PART_OF, Direction.BOTH)
                .evaluator(Evaluators.fromDepth(1))
                .evaluator(Evaluators.toDepth(maxDepth.intValue()))
                .evaluator(Evaluators.includeIfAcceptedByAny(new IpEvaluator(initIp)))
                .traverse(attackedHost);

        // Group paths by IP and map them to result records containing IP,
        // path types and distance
        return StreamSupport
                .stream(traverse.spliterator(), true)
                .collect(Collectors.groupingBy(Path::endNode))
                .entrySet()
                .stream()
                .map(e -> new CloseHostRecord(e.getKey(), e.getValue()));
    }


    /**
     * Result record
     */
    public static final class CloseHostRecord {

        public final String ip;
        public final Long distance;
        public final List<String> path_types;

        CloseHostRecord(Node endNode, List<Path> paths) {
            this.ip = endNode.getProperty("address").toString();
            this.distance = (long) paths.stream().mapToInt(Path::length).min().getAsInt();
            this.path_types = EvaluatePath(paths);
        }

        // determines type of the path
        public List<String> EvaluatePath(List<Path> paths) {
            Set<String> path_types = new HashSet<>();

            for (Path path : paths) {
                if (path.length() == 2) {
                    path_types.add("subnet");
                    return new ArrayList<>(path_types);
                }

                for (Node node : path.nodes()) {
                    if (node.hasLabel(OrganizationUnit)) {
                        path_types.add("organization");
                    }

                    if (node.hasLabel(Contact)) {
                        path_types.add("contact");
                    }
                }
            }
            return new ArrayList<>(path_types);
        }
    }

    /**
     * Evaluator accepts all IP nodes which address property doesn't equal to source IP address.
     */
    private static final class IpEvaluator implements Evaluator {

        private final String sourceIp;

        private IpEvaluator(String sourceIp) {
            this.sourceIp = sourceIp;
        }

        @Override
        public Evaluation evaluate(Path path) {
            var endNode = path.endNode();
            if (endNode.hasLabel(Label.label("IP")) && !endNode.getProperty("address").equals(sourceIp)) {
                return Evaluation.INCLUDE_AND_CONTINUE;
            } else {
                return Evaluation.EXCLUDE_AND_CONTINUE;
            }
        }
    }
}
