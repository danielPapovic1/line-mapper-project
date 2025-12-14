public class Example22 {
    private int alpha = 5;
    private int beta = 10;
    private int gamma = 15;
    private String name;
    public Example22() {
        name = "Example22";
    }
    public int sum() {
        int total = alpha + beta + gamma;
        System.out.println("sum=" + total);
        return total;
    }
    public int diff() {
        int delta = gamma - alpha;
        System.out.println("diff=" + delta);
        return delta;
    }
    public void status() {
        System.out.println("alpha=" + alpha);
        System.out.println("beta=" + beta);
        System.out.println("gamma=" + gamma);
        System.out.println("done");
    }
    public void debug() {
        for (int i = 0; i < 3; i++) {
            System.out.println("debug#" + i);
        }
    }
}
