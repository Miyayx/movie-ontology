package movie;

import com.hp.hpl.jena.query.*;
import com.hp.hpl.jena.rdf.model.RDFNode;

import virtuoso.jena.driver.*;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.LinkedHashMap;

//import lucene3.IndexCKB;
public class MovieVirt {
	String NS = "http://keg.tsinghua.edu.cn/movie/";
	String graphname = "lore4";
	String jdbc = "jdbc:virtuoso://10.1.1.189:1111";
	String[] prefix = { "baidu", "hudong", "enwiki", "zhwiki" };
	VirtGraph set = null;

	public MovieVirt() {
		set = new VirtGraph("keg-movie", "jdbc:virtuoso://10.1.1.189:1111",
				"dba", "dba");
	}

	public HashMap<String,String> query(String q) {
		HashMap<String,String> R = new LinkedHashMap<String,String>();
		Query sparql = QueryFactory.create(q.toString());

		VirtuosoQueryExecution vqe = VirtuosoQueryExecutionFactory.create(
				sparql, set);
		ResultSet results = vqe.execSelect();
		
		while (results.hasNext()) {
			QuerySolution result = results.nextSolution();
			RDFNode p = result.get("p");
			RDFNode s = result.get("o");
			R.put(p.toString(), s.toString());
		}
		return R;

	}

	public static void main(String[] args) throws IOException {
		MovieVirt db = new MovieVirt();
		// db.getAbstract(".\\data\\sparql.txt",".\\data\\result.txt");
		// db.getAbstract(args[1],args[2]);
		// System.out.println(result);
		// keg.getUriByLabel("D:\\java\\xlore\\������.txt");
		String NS = "http://keg.tsinghua.edu.cn/movie/";

//		String query = "select * where {<" + NS + "instance/" + 11500030
//				+ "> <" + NS + "common/summary> ?o}";
		String query = "select * where {<" + NS + "instance/" + 11500030
				+ "> ?p"+" ?o}";
		System.out.println(query.toString());
		db.query(query).toString();
		Query sparql = QueryFactory.create(query.toString());

		VirtGraph set = new VirtGraph("keg-movie",
				"jdbc:virtuoso://10.1.1.189:1111", "dba", "dba");
		VirtuosoQueryExecution vqe = VirtuosoQueryExecutionFactory.create(
				sparql, set);
		String res = "";
		int count = 0;
		ResultSet results = vqe.execSelect();
		while (results.hasNext()) {
			QuerySolution result = results.nextSolution();
			
			RDFNode s = result.get("o");
			res = s.toString();
			count++;
		}
		if (count == 0) {
			res = "";
		}
		System.out.println(res);

	}

	public void getAbstract(String inf, String outf) throws IOException {
		File inFile;
		BufferedReader reader;
		inFile = new File(inf);
		reader = new BufferedReader(new FileReader(inFile));
		String line;

		StringBuffer query = new StringBuffer();
		while ((line = reader.readLine()) != null) {
			query.append(line + "\n");
		}
		reader.close();

		String res = "";
		VirtGraph set = null;
		VirtuosoQueryExecution vqe = null;

		try {
			set = new VirtGraph("keg-movie", "jdbc:virtuoso://10.1.1.189:1111",
					"dba", "dba");

			// String query = "select * where {<" + NS +"instance/" + uri
			// + "> <"+NS+"common/summary> ?o}";

			System.out.println(query.toString());
			Query sparql = QueryFactory.create(query.toString());

			vqe = VirtuosoQueryExecutionFactory.create(sparql, set);

			int count = 0;
			ResultSet results = vqe.execSelect();
			while (results.hasNext()) {
				QuerySolution result = results.nextSolution();
				RDFNode s = result.get("o");
				res = s.toString();
				count++;
			}
			if (count == 0) {
				res = "";
			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			if (vqe != null)
				vqe.close();
			if (set != null)
				set.close();
		}
		// System.out.println(res);
		FileWriter fw = new FileWriter(outf, false);
		fw.write(res);
		fw.close();
	}
}
